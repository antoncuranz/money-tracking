import pytest

from fastapi import HTTPException
from sqlmodel import Session

from core.dataaccess.account_repository import AccountRepository
from core.dataaccess.credit_repository import CreditRepository
from core.dataaccess.exchange_repository import ExchangeRepository
from core.dataaccess.payment_repository import PaymentRepository
from core.dataaccess.store import Store
from core.dataaccess.transaction_repository import TransactionRepository
from exchangerate.business.exchangerate_service import ExchangeRateService
from exchangerate.dataaccess.exchangerate_repository import ExchangeRateRepository
from exchangerate.facade import ExchangeRateFacade
from models import Account, BankAccount, Transaction, User
from statement_match.business.statement_match_service import CandidateTransaction, StatementMatchService
from tests.fixtures import ACCOUNT_1, ALICE_USER, BANK_ACCOUNT_1
from tests.mockclients.exchangerates import MockExchangeRateClient
from tests.mockclients.statement_match import MockPdfExtractor, MockStatementMatchLlmClient


def create_service() -> StatementMatchService:
    return StatementMatchService(
        Store(
            AccountRepository(),
            TransactionRepository(),
            CreditRepository(),
            PaymentRepository(),
            ExchangeRepository(),
        ),
        MockPdfExtractor(),
        MockStatementMatchLlmClient(),
        ExchangeRateFacade(
            ExchangeRateService(
                MockExchangeRateClient(),
                MockExchangeRateClient(),
                ExchangeRateRepository(),
            )
        ),
    )


@pytest.fixture(autouse=True)
def setup(session: Session):
    MockPdfExtractor.reset()
    MockStatementMatchLlmClient.reset()
    session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1)])


def test_match_statement_preserves_one_result_per_transaction(session: Session):
    session.add_all([
        Transaction(
            id=1,
            account_id=1,
            import_id="tx-1",
            date="2024-01-01",
            counterparty="Merchant",
            description="Card purchase 1",
            category="category",
            amount_usd=1000,
            amount_eur=None,
            status=Transaction.Status.POSTED.value,
            fees_and_risk_eur=None,
        ),
        Transaction(
            id=2,
            account_id=1,
            import_id="tx-2",
            date="2024-01-02",
            counterparty="Merchant",
            description="Card purchase 2",
            category="category",
            amount_usd=1000,
            amount_eur=None,
            status=Transaction.Status.POSTED.value,
            fees_and_risk_eur=None,
        ),
    ])
    MockStatementMatchLlmClient.payload = {
        "results": [
            {
                "transaction_id": 2,
                "matched": True,
                "amount_eur": 950,
                "confidence": 0.81,
                "statement_excerpt": "second line",
                "reason": "matched second item",
            },
            {
                "transaction_id": 1,
                "matched": True,
                "amount_eur": 850,
                "confidence": 0.84,
                "statement_excerpt": "first line",
                "reason": "matched first item",
            },
        ]
    }

    response = create_service().match_statement(session, session.get(User, 1), 1, b"pdf")

    assert [result.transaction_id for result in response.results] == [1, 2]
    assert response.results[0].amount_eur == 850
    assert response.results[0].date == "2024-01-01"
    assert response.results[0].amount_usd == 1000
    assert response.results[0].guessed_amount_eur == 909
    assert response.results[0].counterparty == "Merchant"
    assert response.results[0].description == "Card purchase 1"
    assert response.results[1].amount_eur == 950


def test_build_prompt_uses_integer_cent_contract():
    prompt = create_service()._build_prompt(
        "statement text",
        [
            CandidateTransaction(
                transaction_id=1,
                date="2024-01-01",
                amount_usd=234,
                counterparty="Merchant",
                description="Card purchase",
            )
        ],
    )

    assert '"amount_eur": 1144' in prompt
    assert "amount_usd is already known and is in USD cents." in prompt
    assert "Do not return decimal EUR values like 11.44." in prompt
    assert "If the statement does not explicitly show a EUR amount for a candidate, do not infer or fabricate one from amount_usd; prefer matched=false." in prompt


def test_match_statement_accepts_integer_cent_amounts(session: Session):
    session.add(
        Transaction(
            id=1,
            account_id=1,
            import_id="tx-1",
            date="2024-01-01",
            counterparty="Merchant",
            description="Card purchase",
            category="category",
            amount_usd=1000,
            amount_eur=None,
            status=Transaction.Status.POSTED.value,
            fees_and_risk_eur=None,
        )
    )
    MockStatementMatchLlmClient.payload = {
        "results": [
            {
                "transaction_id": 1,
                "matched": True,
                "amount_eur": 1235,
                "confidence": 0.9,
                "statement_excerpt": "line",
                "reason": "matched",
            }
        ]
    }

    response = create_service().match_statement(session, session.get(User, 1), 1, b"pdf")

    assert response.results[0].amount_eur == 1235


def test_match_statement_rejects_decimal_eur_amounts(session: Session):
    session.add(
        Transaction(
            id=1,
            account_id=1,
            import_id="tx-1",
            date="2024-01-01",
            counterparty="Merchant",
            description="Card purchase",
            category="category",
            amount_usd=1000,
            amount_eur=None,
            status=Transaction.Status.POSTED.value,
            fees_and_risk_eur=None,
        )
    )
    MockStatementMatchLlmClient.payload = {
        "results": [
            {
                "transaction_id": 1,
                "matched": True,
                "amount_eur": 12.34,
                "confidence": 0.9,
                "statement_excerpt": "line",
                "reason": "matched",
            }
        ]
    }

    with pytest.raises(HTTPException) as exc_info:
        create_service().match_statement(session, session.get(User, 1), 1, b"pdf")

    assert exc_info.value.status_code == 502


def test_match_statement_rejects_out_of_range_confidence(session: Session):
    session.add(
        Transaction(
            id=1,
            account_id=1,
            import_id="tx-1",
            date="2024-01-01",
            counterparty="Merchant",
            description="Card purchase",
            category="category",
            amount_usd=1000,
            amount_eur=None,
            status=Transaction.Status.POSTED.value,
            fees_and_risk_eur=None,
        )
    )
    MockStatementMatchLlmClient.payload = {
        "results": [
            {
                "transaction_id": 1,
                "matched": True,
                "amount_eur": 1234,
                "confidence": 1.1,
                "statement_excerpt": "line",
                "reason": "matched",
            }
        ]
    }

    with pytest.raises(HTTPException) as exc_info:
        create_service().match_statement(session, session.get(User, 1), 1, b"pdf")

    assert exc_info.value.status_code == 502
