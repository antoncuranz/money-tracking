import pytest
from sqlmodel import Session, select
from fastapi.testclient import TestClient
from sqlalchemy.exc import NoResultFound

from models import Account, Transaction, Credit, CreditTransaction, User, BankAccount
from tests.fixtures import ACCOUNT_1, CREDIT_1, TX_1, TX_2, TX_3, CREDIT_2, ALICE_AUTH, ALICE_USER, \
    BANK_ACCOUNT_1


@pytest.fixture(autouse=True)
def setup(session: Session):
    session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1)])

def test_get_credits(session: Session, client: TestClient):
    # Arrange
    account_id = 1
    session.add(Credit(**CREDIT_1))

    # Act
    response = client.get(f"/api/credits?account={account_id}", headers=ALICE_AUTH)
    parsed = response.json()

    # Assert
    assert response.status_code == 200
    assert len(parsed) == 1


def test_update_credit(session: Session, client, balance_service):
    # Arrange
    credit = Credit(**CREDIT_1)
    session.add(credit)
    tx = Transaction(**TX_1)
    session.add(tx)
    session.commit()

    assert tx.amount_usd == credit.amount_usd

    # Act
    response = client.put(f"/api/credits/{credit.id}?transaction={tx.id}&amount={credit.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 204
    assert balance_service.calc_transaction_remaining(session, tx) == 0
    assert balance_service.calc_credit_remaining(session, credit) == 0


def test_update_credit_amount_larger_than_tx_400(session: Session, client: TestClient):
    # Arrange
    credit = Credit(**CREDIT_1)
    session.add(credit)
    tx = Transaction(**TX_2)
    session.add(tx)
    session.commit()

    assert tx.amount_usd < credit.amount_usd

    # Act
    response = client.put(f"/api/credits/{credit.id}?transaction={tx.id}&amount={credit.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 400


def test_update_credit_amount_larger_than_remaining_tx_400(session: Session, client, balance_service):
    # Arrange
    credit = Credit(**CREDIT_1)
    session.add(credit)
    credit2 = Credit(**CREDIT_2)
    session.add(credit2)
    tx = Transaction(**TX_1)
    session.add(tx)
    session.add(CreditTransaction(credit_id=credit2.id, transaction_id=tx.id, amount=credit2.amount_usd))
    session.commit()

    assert tx.amount_usd == credit.amount_usd
    assert balance_service.calc_transaction_remaining(session, tx) < credit.amount_usd

    # Act
    response = client.put(f"/api/credits/{credit.id}?transaction={tx.id}&amount={credit.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 400


def test_update_credit_amount_larger_than_credit_400(session: Session, client: TestClient):
    # Arrange
    credit = Credit(**CREDIT_1)
    session.add(credit)
    tx = Transaction(**TX_3)
    session.add(tx)
    session.commit()

    assert tx.amount_usd > credit.amount_usd

    # Act
    response = client.put(f"/api/credits/{credit.id}?transaction={tx.id}&amount={tx.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 400


def test_update_credit_on_paid_transaction_400(session: Session, client: TestClient):
    # Arrange
    credit = Credit(**CREDIT_1)
    session.add(credit)
    tx = Transaction(**TX_1)
    session.add(tx)
    tx.status_enum = Transaction.Status.PAID
    session.add(tx)
    session.add(CreditTransaction(credit_id=credit.id, transaction_id=tx.id, amount=1))
    session.commit()

    # Act
    response = client.put(f"/api/credits/{credit.id}?transaction={tx.id}&amount={credit.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 400


def test_update_credit_delete_credit_transaction(session: Session, client: TestClient):
    # Arrange
    credit = Credit(**CREDIT_1)
    session.add(credit)
    tx = Transaction(**TX_1)
    session.add(tx)
    session.add(CreditTransaction(credit_id=credit.id, transaction_id=tx.id, amount=1))
    session.commit()

    # Act
    response = client.put(f"/api/credits/{credit.id}?transaction={tx.id}&amount={0}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 204
    session.exec(select(Credit)).one()
    session.exec(select(Transaction)).one()
    with pytest.raises(NoResultFound):
        session.exec(select(CreditTransaction)).one()

def test_update_credit_reduce_amount(session: Session, client: TestClient):
    # Arrange
    credit = Credit(**CREDIT_1)
    session.add(credit)
    tx = Transaction(**TX_1)
    session.add(tx)
    session.add(CreditTransaction(credit_id=credit.id, transaction_id=tx.id, amount=credit.amount_usd))
    session.commit()

    assert tx.amount_usd == credit.amount_usd

    # Act
    response = client.put(f"/api/credits/{credit.id}?transaction={tx.id}&amount={credit.amount_usd-10}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 204


def test_get_usable_credits(session: Session, client: TestClient):
    # Arrange
    account_id = 1
    credit = Credit(**CREDIT_1)
    session.add(credit)
    tx = Transaction(**TX_1)
    session.add(tx)
    tx.status_enum = Transaction.Status.PAID
    tx.amount_usd = credit.amount_usd
    session.add(tx)
    session.add(CreditTransaction(credit_id=credit.id, transaction_id=tx.id, amount=credit.amount_usd))
    session.commit()

    assert tx.amount_usd == credit.amount_usd

    credit2 = Credit(**CREDIT_2)

    session.add(credit2)

    # Act
    response = client.get(f"/api/credits?account={account_id}&usable=true", headers=ALICE_AUTH)
    parsed = response.json()

    # Assert
    assert response.status_code == 200
    assert len(parsed) == 1
    assert parsed[0]["id"] == credit2.id
