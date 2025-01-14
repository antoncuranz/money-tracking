from backend.models import Account, Transaction, Credit, Payment, CreditTransaction, User
from backend.tests.fixtures import ACCOUNT_1, ALICE_AUTH, ALICE_USER
import pytest
from peewee import DoesNotExist


# @with_test_db((Account, Transaction,))
# def test_import_transactions_mfa(app, client, teller_mock):
#     # Arrange
#     account_id = Account.create(**ACCOUNT_1)
#     teller_mock.set_mfa_required(True)
#
#     # Act
#     try:
#         response = client.post(f"/api/import/{account_id}", headers=ALICE_USER)
#     finally:
#         teller_mock.set_mfa_required(False)
#
#     # Assert
#     assert response.status_code == 418


def test_import_transactions(client):
    # Arrange
    User.create(**ALICE_USER)
    account = Account.create(**ACCOUNT_1)

    # Act
    response = client.post(f"/api/import/{account}", headers=ALICE_AUTH)
    transactions = Transaction.select()
    credits = Credit.select()
    payments = Payment.select()

    # Assert
    assert response.status_code == 204
    assert len(transactions) == 2
    assert transactions[0].status_enum == Transaction.Status.POSTED
    # assert transactions[1].status_enum == Transaction.Status.PENDING

    assert len(credits) == 1
    assert credits[0].amount_usd > 0

    assert len(payments) == 1
    assert payments[0].amount_usd > 0

    return  # TODO: MX does not support pending transactions

    # Arrange 2
    # Delete vanished pending transactions and linked CreditTransactions
    CreditTransaction.create(credit=credits[0], transaction=transactions[1], amount=1)
    CreditTransaction.get()
    quiltt_mock.set_transactions(account.import_id, [])

    # Act 2
    response = client.post(f"/api/import/{account}", headers=ALICE_AUTH)
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