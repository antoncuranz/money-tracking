import json

from backend import Account, User
from backend.tests.conftest import with_test_db
from backend.tests.fixtures import ACCOUNT_1, ALICE_AUTH, ALICE_USER


@with_test_db((User, Account,))
def test_get_accounts(client):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)

    # Act
    response = client.get("/api/accounts", headers=ALICE_AUTH)
    parsed = json.loads(response.data)

    # Assert
    assert len(parsed) == 1
    assert parsed[0]["actual_id"] == ACCOUNT_1["actual_id"]
    assert parsed[0]["teller_id"] == ACCOUNT_1["teller_id"]
    assert parsed[0]["name"] == ACCOUNT_1["name"]
    assert parsed[0]["institution"] == ACCOUNT_1["institution"]


@with_test_db((User, Account,))
def test_get_balances(client, teller_mock):
    # Arrange
    User.create(**ALICE_USER)
    account_id = Account.create(**ACCOUNT_1)

    # Act
    response = client.get(f"/api/accounts/{account_id}/balances", headers=ALICE_AUTH)
    parsed = json.loads(response.data)

    # Assert
    assert response.status_code == 200
    assert parsed["available"] == "123.45"
    assert parsed["ledger"] == "123.45"
