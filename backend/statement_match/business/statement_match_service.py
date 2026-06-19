import json
import logging
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, ValidationError
from sqlmodel import Session

from core.dataaccess.store import Store
from exchangerate.facade import ExchangeRateFacade
from models import Transaction, User
from statement_match.adapter.llm_client import LlmProviderError, StatementMatchLlmClient
from statement_match.adapter.pdf_extractor import PdfExtractionError, PdfExtractor

logger = logging.getLogger(__name__)

MAX_STATEMENT_TEXT_LENGTH = 100000
MAX_CANDIDATE_COUNT = 200


class CandidateTransaction(BaseModel):
    transaction_id: int
    date: str
    amount_usd: int
    counterparty: str
    description: str


class StatementMatchResult(BaseModel):
    transaction_id: int
    date: str
    amount_usd: int
    amount_eur: int | None
    guessed_amount_eur: int | None
    counterparty: str
    description: str
    matched: bool
    confidence: float
    statement_excerpt: str | None
    reason: str


class StatementMatchResponse(BaseModel):
    account_id: int
    results: list[StatementMatchResult]


class RawStatementMatchResult(BaseModel):
    transaction_id: int
    amount_eur: Any = None
    matched: bool
    confidence: float
    statement_excerpt: str | None = None
    reason: str


class RawStatementMatchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    results: list[RawStatementMatchResult]


@dataclass
class OversizedStatementMatchError(Exception):
    message: str


class StatementMatchService:
    def __init__(
        self,
        store: Annotated[Store, Depends()],
        pdf_extractor: Annotated[PdfExtractor, Depends()],
        llm_client: Annotated[StatementMatchLlmClient, Depends()],
        exchangerate: Annotated[ExchangeRateFacade, Depends()],
    ):
        self.store = store
        self.pdf_extractor = pdf_extractor
        self.llm_client = llm_client
        self.exchangerate = exchangerate

    def match_statement(self, session: Session, user: User, account_id: int, pdf_content: bytes) -> StatementMatchResponse:
        account = self.store.get_account(session, user, account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        candidates = self.store.get_posted_transactions_missing_amount_eur_by_account(session, account_id)
        logger.info("statement_match_start account_id=%s candidate_count=%s", account_id, len(candidates))

        if not candidates:
            return StatementMatchResponse(account_id=account_id, results=[])

        try:
            statement_text = self.pdf_extractor.extract_text(pdf_content)
        except PdfExtractionError as exc:
            logger.warning("statement_match_failed account_id=%s stage=pdf error=%s", account_id, exc)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        logger.info("statement_match_pdf_extracted account_id=%s text_length=%s", account_id, len(statement_text))

        candidate_payload = [self._to_candidate_payload(candidate) for candidate in candidates]

        try:
            self._check_size(statement_text, candidate_payload)
        except OversizedStatementMatchError as exc:
            logger.warning("statement_match_failed account_id=%s stage=size_guard error=%s", account_id, exc.message)
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=exc.message) from exc

        prompt = self._build_prompt(statement_text, candidate_payload)

        try:
            raw_response = self.llm_client.match_statement(prompt)
            validated = self._validate_results(candidate_payload, raw_response)
        except (LlmProviderError, ValidationError, ValueError) as exc:
            logger.warning("statement_match_failed account_id=%s stage=provider error=%s", account_id, exc, exc_info=True)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Statement match provider failed.") from exc

        logger.info(
            "statement_match_llm_completed account_id=%s candidate_count=%s model=%s",
            account_id,
            len(candidate_payload),
            self.llm_client.model,
        )

        return StatementMatchResponse(
            account_id=account_id,
            results=self._enrich_results(session, candidates, validated),
        )

    def _to_candidate_payload(self, transaction: Transaction) -> CandidateTransaction:
        return CandidateTransaction(
            transaction_id=transaction.id,
            date=transaction.date.isoformat(),
            amount_usd=transaction.amount_usd,
            counterparty=transaction.counterparty,
            description=transaction.description,
        )

    def _check_size(self, statement_text: str, candidates: list[CandidateTransaction]):
        if len(statement_text) > MAX_STATEMENT_TEXT_LENGTH:
            raise OversizedStatementMatchError("Statement text is too large for single-pass matching.")

        if len(candidates) > MAX_CANDIDATE_COUNT:
            raise OversizedStatementMatchError("Too many candidate transactions for single-pass matching.")

    def _build_prompt(self, statement_text: str, candidates: list[CandidateTransaction]) -> str:
        candidate_json = json.dumps([candidate.model_dump(mode="json") for candidate in candidates], indent=2)
        return (
            "Match each candidate transaction against the statement text and determine the original EUR amount. "
            "Prefer matched=false over weak guesses.\n\n"
            "Return JSON with exactly this shape:\n"
            "{\n"
            '  "results": [\n'
            "    {\n"
            '      "transaction_id": 123,\n'
            '      "matched": true,\n'
            '      "amount_eur": 1144,\n'
            '      "confidence": 0.95,\n'
            '      "statement_excerpt": "...",\n'
            '      "reason": "short explanation"\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Rules:\n"
            "- Return exactly one result for every candidate transaction.\n"
            "- Use every provided transaction_id exactly once.\n"
            "- Do not add extra transactions.\n"
            "- confidence must be a number between 0 and 1.\n"
            "- If matched is false, amount_eur must be null.\n"
            "- If matched is true, amount_eur must be the original EUR amount from the statement, returned in integer cents.\n"
            "- amount_usd is already known and is in USD cents. Use it only to identify the transaction, not as the answer.\n"
            "- Some transactions (including fees) may have been made in USD. If no EUR amount is shown for such a transaction, that is okay. Do not infer a EUR amount from amount_usd; return matched=false.\n"
            "- Example: if the statement shows EUR 11.44, return amount_eur: 1144.\n"
            "- Do not return decimal EUR values like 11.44.\n"
            "- It is extremely unlikely that amount_eur equals amount_usd. If the best candidate just mirrors amount_usd, prefer matched=false.\n"
            "- Currency symbols may be unreliable.\n"
            "- statement_excerpt should quote or summarize the most relevant nearby statement text.\n"
            "- reason should briefly explain the decision, especially when matched is false.\n"
            "- Consider slight merchant-name differences, nearby date shifts, and repeated same-amount transactions carefully.\n\n"
            f"Candidate transactions:\n{candidate_json}\n\n"
            f"Statement text:\n{statement_text}"
        )

    def _validate_results(self, candidates: list[CandidateTransaction], raw_response: dict[str, Any]) -> list[RawStatementMatchResult]:
        payload = RawStatementMatchResponse.model_validate(raw_response)
        candidate_ids = [candidate.transaction_id for candidate in candidates]
        result_ids = [result.transaction_id for result in payload.results]

        if len(result_ids) != len(candidate_ids):
            raise ValueError("Statement match result count does not match candidates.")

        if len(set(result_ids)) != len(result_ids):
            raise ValueError("Statement match response contains duplicate transaction ids.")

        if set(result_ids) != set(candidate_ids):
            raise ValueError("Statement match response does not match candidate transaction ids.")

        normalized_results = []
        for raw_result in payload.results:
            if not 0 <= raw_result.confidence <= 1:
                raise ValueError("Statement match confidence is out of range.")

            amount_eur = self._normalize_amount_eur(raw_result.amount_eur)
            if raw_result.matched and amount_eur is None:
                raise ValueError("Matched statement result is missing amount_eur.")
            if not raw_result.matched and amount_eur is not None:
                raise ValueError("Unmatched statement result must not include amount_eur.")

            normalized_results.append(
                RawStatementMatchResult(
                    transaction_id=raw_result.transaction_id,
                    amount_eur=amount_eur,
                    matched=raw_result.matched,
                    confidence=raw_result.confidence,
                    statement_excerpt=raw_result.statement_excerpt,
                    reason=raw_result.reason,
                )
            )

        results_by_id = {result.transaction_id: result for result in normalized_results}
        return [results_by_id[candidate_id] for candidate_id in candidate_ids]

    def _enrich_results(
        self,
        session: Session,
        transactions: list[Transaction],
        results: list[RawStatementMatchResult],
    ) -> list[StatementMatchResult]:
        results_by_id = {result.transaction_id: result for result in results}

        enriched_results = []
        for transaction in transactions:
            guessed_amount_eur = self.exchangerate.guess_amount_eur(session, transaction)
            result = results_by_id[transaction.id]
            enriched_results.append(
                StatementMatchResult(
                    transaction_id=transaction.id,
                    date=transaction.date.isoformat(),
                    amount_usd=transaction.amount_usd,
                    amount_eur=result.amount_eur,
                    guessed_amount_eur=guessed_amount_eur,
                    counterparty=transaction.counterparty,
                    description=transaction.description,
                    matched=result.matched,
                    confidence=result.confidence,
                    statement_excerpt=result.statement_excerpt,
                    reason=result.reason,
                )
            )

        return enriched_results

    def _normalize_amount_eur(self, value: Any) -> int | None:
        if value is None:
            return None

        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("Statement match amount_eur is invalid.") from exc

        if decimal_value != decimal_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP):
            raise ValueError("Statement match amount_eur must be integer cents.")

        return int(decimal_value)
