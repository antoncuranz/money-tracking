import json

from backend import Account, Transaction, Credit, CreditTransaction
from tests.conftest import with_test_db
from tests.fixtures import ACCOUNT_1, CREDIT_1, TX_1, TX_2, TX_3


@with_test_db((Account, Credit, CreditTransaction, Transaction,))
def test_get_credits(app, client):
    # Arrange
    account = Account.create(**ACCOUNT_1)
    Credit.create(**CREDIT_1)

    # Act
    response = client.get(f"/api/accounts/{account}/credits")
    parsed = json.loads(response.data)

    # Assert
    assert response.status_code == 200
    assert len(parsed) == 1


@with_test_db((Account, Credit, CreditTransaction, Transaction,))
def test_update_credit(app, client, balance_service):
    # Arrange
    account = Account.create(**ACCOUNT_1)
    credit = Credit.create(**CREDIT_1)
    tx = Transaction.create(**TX_1)

    assert tx.amount_usd == credit.amount_usd

    # Act
    response = client.put(f"/api/accounts/{account}/credits/{credit}?transaction={tx}&amount={credit.amount_usd}")

    # Assert
    assert response.status_code == 204
    assert balance_service.calc_transaction_remaining(tx) == 0
    assert balance_service.calc_credit_remaining(credit) == 0


@with_test_db((Account, Credit, CreditTransaction, Transaction,))
def test_update_credit_2(app, client, balance_service):
    # amount is larger than transaction amount (TODO: use remaining amount instead)
    # Arrange
    account = Account.create(**ACCOUNT_1)
    credit = Credit.create(**CREDIT_1)
    tx = Transaction.create(**TX_2)

    assert tx.amount_usd < credit.amount_usd

    # Act
    response = client.put(f"/api/accounts/{account}/credits/{credit}?transaction={tx}&amount={credit.amount_usd}")

    # Assert
    assert response.status_code == 500


@with_test_db((Account, Credit, CreditTransaction, Transaction,))
def test_update_credit_2(app, client, balance_service):
    # amount is larger than credit amount
    # Arrange
    account = Account.create(**ACCOUNT_1)
    credit = Credit.create(**CREDIT_1)
    tx = Transaction.create(**TX_3)

    assert tx.amount_usd > credit.amount_usd

    # Act
    response = client.put(f"/api/accounts/{account}/credits/{credit}?transaction={tx}&amount={tx.amount_usd}")

    # Assert
    assert response.status_code == 500


# TODO: delete CreditTransaction using amount = 0
# TODO: update CreditTransaction amount
