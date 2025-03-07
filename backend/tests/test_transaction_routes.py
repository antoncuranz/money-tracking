from backend.models import Account, User, Transaction
from backend.tests.fixtures import ACCOUNT_1, ALICE_AUTH, ALICE_USER, TX_1


def test_get_all_transactions(client):
    # TODO
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


def test_clear_transaction_amount_eur(client):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)
    Transaction.create(**TX_1)
    assert Transaction.get(Transaction.id == 1).amount_eur is not None

    # Act
    response = client.put("/api/transactions/1", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 200
    assert Transaction.get(Transaction.id == 1).amount_eur is None
