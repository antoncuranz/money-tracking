from models import Account, User, BankAccount
from tests.fixtures import ACCOUNT_1, ALICE_AUTH, ALICE_USER, BANK_ACCOUNT_1

from sqlmodel import Session
from fastapi.testclient import TestClient

def test_get_accounts(session: Session, client: TestClient):
    # Arrange
    session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1)])
    session.commit()

    # Act
    response = client.get("/api/accounts", headers=ALICE_AUTH)
    parsed = response.json()

    # Assert
    print(parsed)
    assert len(parsed) == 1
    assert parsed[0]["actual_id"] == ACCOUNT_1["actual_id"]
    assert parsed[0]["name"] == ACCOUNT_1["name"]
    assert parsed[0]["institution"] == ACCOUNT_1["institution"]
