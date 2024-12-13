import json

import pytest
from peewee import DoesNotExist

from backend.models import Account, Transaction, Credit, CreditTransaction, Payment, User
from backend.tests.conftest import with_test_db
from backend.tests.fixtures import ACCOUNT_1, CREDIT_1, TX_1, TX_2, TX_3, CREDIT_2, ALICE_AUTH, ALICE_USER


@with_test_db((User, Account, Credit, CreditTransaction, Transaction, Payment))
def test_get_credits(app, client):
    # Arrange
    User.create(**ALICE_USER)
    account = Account.create(**ACCOUNT_1)
    Credit.create(**CREDIT_1)

    # Act
    response = client.get(f"/api/credits?account={account}", headers=ALICE_AUTH)
    parsed = json.loads(response.data)

    # Assert
    assert response.status_code == 200
    assert len(parsed) == 1


@with_test_db((User, Account, Credit, CreditTransaction, Transaction, Payment))
def test_update_credit(app, client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)
    credit = Credit.create(**CREDIT_1)
    tx = Transaction.create(**TX_1)

    assert tx.amount_usd == credit.amount_usd

    # Act
    response = client.put(f"/api/credits/{credit}?transaction={tx}&amount={credit.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 204
    assert balance_service.calc_transaction_remaining(tx) == 0
    assert balance_service.calc_credit_remaining(credit) == 0


@with_test_db((User, Account, Credit, CreditTransaction, Transaction, Payment))
def test_update_credit_amount_larger_than_tx_500(app, client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)
    credit = Credit.create(**CREDIT_1)
    tx = Transaction.create(**TX_2)

    assert tx.amount_usd < credit.amount_usd

    # Act
    response = client.put(f"/api/credits/{credit}?transaction={tx}&amount={credit.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 500


@with_test_db((User, Account, Credit, CreditTransaction, Transaction, Payment))
def test_update_credit_amount_larger_than_remaining_tx_500(app, client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)
    credit = Credit.create(**CREDIT_1)
    credit2 = Credit.create(**CREDIT_2)
    tx = Transaction.create(**TX_1)
    CreditTransaction.create(credit=credit2, transaction=tx, amount=credit2.amount_usd)

    assert tx.amount_usd == credit.amount_usd
    assert balance_service.calc_transaction_remaining(tx) < credit.amount_usd

    # Act
    response = client.put(f"/api/credits/{credit}?transaction={tx}&amount={credit.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 500


@with_test_db((User, Account, Credit, CreditTransaction, Transaction, Payment))
def test_update_credit_amount_larger_than_credit_500(app, client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)
    credit = Credit.create(**CREDIT_1)
    tx = Transaction.create(**TX_3)

    assert tx.amount_usd > credit.amount_usd

    # Act
    response = client.put(f"/api/credits/{credit}?transaction={tx}&amount={tx.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 500


@with_test_db((User, Account, Credit, CreditTransaction, Transaction, Payment))
def test_update_credit_on_paid_transaction_404(app, client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)
    credit = Credit.create(**CREDIT_1)
    tx = Transaction.create(**TX_1)
    tx.status_enum = Transaction.Status.PAID
    tx.save()
    CreditTransaction.create(credit=credit, transaction=tx, amount=1)

    # Act
    response = client.put(f"/api/credits/{credit}?transaction={tx}&amount={credit.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 404


@with_test_db((User, Account, Credit, CreditTransaction, Transaction, Payment))
def test_update_credit_delete_credit_transaction(app, client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)
    credit = Credit.create(**CREDIT_1)
    tx = Transaction.create(**TX_1)
    CreditTransaction.create(credit=credit, transaction=tx, amount=1)

    # Act
    response = client.put(f"/api/credits/{credit}?transaction={tx}&amount={0}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 204
    Credit.get()
    Transaction.get()
    with pytest.raises(DoesNotExist):
        CreditTransaction.get()

@with_test_db((User, Account, Credit, CreditTransaction, Transaction, Payment))
def test_update_credit_reduce_amount(app, client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)
    credit = Credit.create(**CREDIT_1)
    tx = Transaction.create(**TX_1)
    CreditTransaction.create(credit=credit, transaction=tx, amount=credit.amount_usd)

    assert tx.amount_usd == credit.amount_usd

    # Act
    response = client.put(f"/api/credits/{credit}?transaction={tx}&amount={credit.amount_usd-10}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 204


@with_test_db((User, Account, Credit, CreditTransaction, Transaction, Payment))
def test_get_usable_credits(app, client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    account = Account.create(**ACCOUNT_1)
    credit = Credit.create(**CREDIT_1)
    tx = Transaction.create(**TX_1)
    tx.status_enum = Transaction.Status.PAID
    tx.amount_usd = credit.amount_usd
    tx.save()
    CreditTransaction.create(credit=credit, transaction=tx, amount=credit.amount_usd)

    assert tx.amount_usd == credit.amount_usd

    credit2 = Credit.create(**CREDIT_2)

    # Act
    response = client.get(f"/api/credits?account={account}&usable=true", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["id"] == credit2.id
