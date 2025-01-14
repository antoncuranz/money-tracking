from backend.models import Account, User
from backend.tests.fixtures import ACCOUNT_1, ALICE_AUTH, ALICE_USER


def test_get_accounts(client):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)

    # Act
    response = client.get("/api/accounts", headers=ALICE_AUTH)
    parsed = response.json()

    # Assert
    assert len(parsed) == 1
    assert parsed[0]["actual_id"] == ACCOUNT_1["actual_id"]
    assert parsed[0]["import_id"] == ACCOUNT_1["import_id"]
    assert parsed[0]["name"] == ACCOUNT_1["name"]
    assert parsed[0]["institution"] == ACCOUNT_1["institution"]

