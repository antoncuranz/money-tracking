from models import Account, User, Transaction, BankAccount
from tests.fixtures import ACCOUNT_1, ALICE_AUTH, ALICE_USER, TX_1, BANK_ACCOUNT_1

from sqlmodel import Session, select
from fastapi.testclient import TestClient
import pytest


@pytest.fixture(autouse=True)
def setup(session: Session):
    session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1)])


def test_get_all_transactions(session: Session, client: TestClient):
    # TODO
    # Arrange

    # Act
    response = client.get("/api/accounts", headers=ALICE_AUTH)
    parsed = response.json()

    # Assert
    assert len(parsed) == 1
    assert parsed[0]["actual_id"] == ACCOUNT_1["actual_id"]
    assert parsed[0]["import_id"] == ACCOUNT_1["import_id"]
    assert parsed[0]["name"] == ACCOUNT_1["name"]
    assert parsed[0]["institution"] == ACCOUNT_1["institution"]


def test_clear_transaction_amount_eur(session: Session, client: TestClient):
    # Arrange
    session.add(Transaction(**TX_1))
    assert session.exec(select(Transaction).where(Transaction.id == 1)).one().amount_eur is not None

    # Act
    response = client.put("/api/transactions/1", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 204
    assert session.exec(select(Transaction).where(Transaction.id == 1)).one().amount_eur is None
