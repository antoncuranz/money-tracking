import json

from backend import Account, Transaction, ExchangeRate
from tests.conftest import with_test_db
from tests.fixtures import ACCOUNT_1, TELLER_TX_1


@with_test_db((Account, Transaction,))
def test_import_transactions_mfa(app, client, teller_mock):
    # Arrange
    account_id = Account.create(**ACCOUNT_1)
    teller_mock.set_mfa_required(True)

    # Act
    try:
        response = client.post(f"/api/import/{account_id}")
    finally:
        teller_mock.set_mfa_required(False)

    # Assert
    assert response.status_code == 418


@with_test_db((Account, Transaction, ExchangeRate))
def test_import_transactions(app, client, teller_mock, mastercard_mock):
    # Arrange
    account_id = Account.create(**ACCOUNT_1)

    # Act
    response = client.post(f"/api/import/{account_id}")
    transactions = Transaction.select()

    # Assert
    assert response.status_code == 204
    assert len(transactions) == 1
    assert transactions[0].teller_id == TELLER_TX_1["id"]
