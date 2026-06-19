import json

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from models import Account, BankAccount, Transaction, User
from statement_match.adapter.llm_client import LlmProviderError, StatementMatchLlmClient
from statement_match.adapter.pdf_extractor import PdfExtractor
from tests.fixtures import ALICE_AUTH, ALICE_USER, BANK_ACCOUNT_1, BOB_AUTH, BOB_USER
from tests.mockclients.statement_match import MockPdfExtractor, MockStatementMatchLlmClient


def make_transaction(id: int, account_id: int, status: int, amount_eur: int | None):
    return Transaction(
        id=id,
        account_id=account_id,
        import_id=f"tx-{id}",
        date=f"2024-01-{id:02d}",
        counterparty=f"Counterparty {id}",
        description=f"Description {id}",
        category="category",
        amount_usd=1000 + id,
        amount_eur=amount_eur,
        status=status,
        fees_and_risk_eur=None,
    )


@pytest.fixture(autouse=True)
def setup(session: Session, override_statement_match_dependencies):
    session.add_all(
        [
            User(**ALICE_USER),
            User(**BOB_USER),
            BankAccount(**BANK_ACCOUNT_1),
            Account(**dict(id=1, user_id=1, actual_id="actual-1", name="Alice Account", institution="Bank", import_id="account-1", bank_account_id=1)),
            Account(**dict(id=2, user_id=2, actual_id="actual-2", name="Bob Account", institution="Bank", import_id="account-2")),
        ]
    )


def parse_candidates(prompt: str):
    marker = "Candidate transactions:\n"
    tail_marker = "\n\nStatement text:\n"
    start = prompt.index(marker) + len(marker)
    end = prompt.index(tail_marker)
    return json.loads(prompt[start:end])


def test_match_statement_success(session: Session, client: TestClient):
    session.add(make_transaction(1, 1, Transaction.Status.POSTED.value, None))
    MockStatementMatchLlmClient.payload = {
        "results": [
            {
                "transaction_id": 1,
                "matched": True,
                "amount_eur": 1234,
                "confidence": 0.98,
                "statement_excerpt": "merchant 12,34 EUR",
                "reason": "exact amount and merchant",
            }
        ]
    }

    response = client.post(
        "/api/statement-match/1",
        headers=ALICE_AUTH,
        files={"file": ("statement.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "account_id": 1,
        "results": [
            {
                "transaction_id": 1,
                "date": "2024-01-01",
                "amount_usd": 1001,
                "amount_eur": 1234,
                "guessed_amount_eur": 909,
                "counterparty": "Counterparty 1",
                "description": "Description 1",
                "matched": True,
                "confidence": 0.98,
                "statement_excerpt": "merchant 12,34 EUR",
                "reason": "exact amount and merchant",
            }
        ],
    }


def test_match_statement_returns_enriched_unmatched_row(session: Session, client: TestClient):
    session.add(make_transaction(1, 1, Transaction.Status.POSTED.value, None))
    MockStatementMatchLlmClient.payload = {
        "results": [
            {
                "transaction_id": 1,
                "matched": False,
                "amount_eur": None,
                "confidence": 0.2,
                "statement_excerpt": None,
                "reason": "not found",
            }
        ]
    }

    response = client.post(
        "/api/statement-match/1",
        headers=ALICE_AUTH,
        files={"file": ("statement.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["results"] == [
        {
            "transaction_id": 1,
            "date": "2024-01-01",
            "amount_usd": 1001,
            "amount_eur": None,
            "guessed_amount_eur": 909,
            "counterparty": "Counterparty 1",
            "description": "Description 1",
            "matched": False,
            "confidence": 0.2,
            "statement_excerpt": None,
            "reason": "not found",
        }
    ]


def test_match_statement_only_sends_posted_transactions_missing_amount(session: Session, client: TestClient):
    session.add_all(
        [
            make_transaction(1, 1, Transaction.Status.POSTED.value, None),
            make_transaction(2, 1, Transaction.Status.POSTED.value, 500),
            make_transaction(3, 1, Transaction.Status.PENDING.value, None),
            make_transaction(4, 1, Transaction.Status.PAID.value, None),
            make_transaction(5, 2, Transaction.Status.POSTED.value, None),
        ]
    )
    MockStatementMatchLlmClient.payload = {
        "results": [
            {
                "transaction_id": 1,
                "matched": False,
                "amount_eur": None,
                "confidence": 0.2,
                "statement_excerpt": None,
                "reason": "not found",
            }
        ]
    }

    response = client.post(
        "/api/statement-match/1",
        headers=ALICE_AUTH,
        files={"file": ("statement.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 200
    assert len(MockStatementMatchLlmClient.prompts) == 1
    assert parse_candidates(MockStatementMatchLlmClient.prompts[0]) == [
        {
            "transaction_id": 1,
            "date": "2024-01-01",
            "amount_usd": 1001,
            "counterparty": "Counterparty 1",
            "description": "Description 1",
        }
    ]


def test_match_statement_returns_404_for_unknown_account(client: TestClient):
    response = client.post(
        "/api/statement-match/999",
        headers=ALICE_AUTH,
        files={"file": ("statement.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 404


def test_match_statement_returns_404_for_unauthorized_account(client: TestClient):
    response = client.post(
        "/api/statement-match/2",
        headers=BOB_AUTH,
        files={"file": ("statement.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 200

    response = client.post(
        "/api/statement-match/1",
        headers=BOB_AUTH,
        files={"file": ("statement.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 404


def test_match_statement_returns_empty_results_without_provider_call(client: TestClient):
    response = client.post(
        "/api/statement-match/1",
        headers=ALICE_AUTH,
        files={"file": ("statement.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json() == {"account_id": 1, "results": []}
    assert MockStatementMatchLlmClient.prompts == []


def test_match_statement_returns_400_for_unreadable_pdf(session: Session, client: TestClient):
    from main import app

    app.dependency_overrides.pop(PdfExtractor, None)
    session.add(make_transaction(1, 1, Transaction.Status.POSTED.value, None))

    response = client.post(
        "/api/statement-match/1",
        headers=ALICE_AUTH,
        files={"file": ("statement.pdf", b"not-a-pdf", "application/pdf")},
    )

    app.dependency_overrides[PdfExtractor] = MockPdfExtractor

    assert response.status_code == 400


def test_match_statement_returns_413_for_oversized_request(session: Session, client: TestClient):
    session.add(make_transaction(1, 1, Transaction.Status.POSTED.value, None))
    MockPdfExtractor.text = "a" * 100001

    response = client.post(
        "/api/statement-match/1",
        headers=ALICE_AUTH,
        files={"file": ("statement.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 413
    assert MockStatementMatchLlmClient.prompts == []


def test_match_statement_returns_502_for_provider_failure(session: Session, client: TestClient):
    session.add(make_transaction(1, 1, Transaction.Status.POSTED.value, None))
    MockStatementMatchLlmClient.error = LlmProviderError("boom")

    response = client.post(
        "/api/statement-match/1",
        headers=ALICE_AUTH,
        files={"file": ("statement.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 502


def test_match_statement_returns_502_for_invalid_provider_payload(session: Session, client: TestClient):
    session.add(make_transaction(1, 1, Transaction.Status.POSTED.value, None))
    MockStatementMatchLlmClient.payload = {"results": []}

    response = client.post(
        "/api/statement-match/1",
        headers=ALICE_AUTH,
        files={"file": ("statement.pdf", b"%PDF-test", "application/pdf")},
    )

    assert response.status_code == 502
