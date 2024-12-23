import json

from backend import BankAccount
from backend.models import Account, Transaction, User
from backend.tests.conftest import with_test_db
from backend.tests.fixtures import ACCOUNT_1, ALICE_AUTH, ALICE_USER


@with_test_db((User, Account, BankAccount, Transaction))
def test_get_all_transactions(client, transaction_service):
    # TODO
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)

    # Act
    response = client.get("/api/accounts", headers=ALICE_AUTH)
    parsed = json.loads(response.data)

    # Assert
    assert len(parsed) == 1
    assert parsed[0]["actual_id"] == ACCOUNT_1["actual_id"]
    assert parsed[0]["import_id"] == ACCOUNT_1["import_id"]
    assert parsed[0]["name"] == ACCOUNT_1["name"]
    assert parsed[0]["institution"] == ACCOUNT_1["institution"]
