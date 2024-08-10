from backend import Account, Transaction, ExchangeRate, Credit, Payment, CreditTransaction, ExchangePayment, Exchange
from backend.tests.conftest import with_test_db
from backend.tests.fixtures import ACCOUNT_1
import pytest
from peewee import DoesNotExist


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


@with_test_db((Account, Credit, CreditTransaction, Transaction, Exchange, ExchangePayment, Payment, ExchangeRate))
def test_import_transactions(app, client, teller_mock, exchangerates_mock, actual_mock):
    # Arrange
    account = Account.create(**ACCOUNT_1)

    # Act
    response = client.post(f"/api/import/{account}")
    transactions = Transaction.select()
    credits = Credit.select()
    payments = Payment.select()

    # Assert
    assert response.status_code == 204
    assert len(transactions) == 2
    assert transactions[0].status_enum == Transaction.Status.POSTED
    assert transactions[1].status_enum == Transaction.Status.PENDING

    assert len(credits) == 1
    assert credits[0].amount_usd > 0

    assert len(payments) == 1
    assert payments[0].amount_usd > 0

    # Arrange 2
    # Delete vanished pending transactions and linked CreditTransactions
    CreditTransaction.create(credit=credits[0], transaction=transactions[1], amount=1)
    CreditTransaction.get()
    teller_mock.set_transactions(account.teller_id, [])

    # Act 2
    response = client.post(f"/api/import/{account}")
    transactions = Transaction.select()
    credits = Credit.select()
    payments = Payment.select()

    # Assert 2
    assert response.status_code == 204
    assert len(transactions) == 1
    assert len(credits) == 1
    assert len(payments) == 1

    with pytest.raises(DoesNotExist):
        CreditTransaction.get()