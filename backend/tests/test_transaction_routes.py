import json

from backend import Account, Transaction
from backend.tests.conftest import with_test_db
from backend.tests.fixtures import ACCOUNT_1, ALICE_USER


@with_test_db((Account, Transaction))
def test_get_all_transactions(client):
    # TODO
    # Arrange
    Account.create(**ACCOUNT_1)

    # Act
    response = client.get("/api/accounts", headers=ALICE_USER)
    parsed = json.loads(response.data)

    # Assert
    assert len(parsed) == 1
    assert parsed[0]["actual_id"] == ACCOUNT_1["actual_id"]
    assert parsed[0]["teller_id"] == ACCOUNT_1["teller_id"]
    assert parsed[0]["name"] == ACCOUNT_1["name"]
    assert parsed[0]["institution"] == ACCOUNT_1["institution"]
