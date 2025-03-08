from models import Account, Transaction, Credit, Payment, CreditTransaction, User, BankAccount
from tests.fixtures import ACCOUNT_1, ALICE_AUTH, ALICE_USER, BANK_ACCOUNT_1
import pytest

from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def setup(session: Session):
    session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1)])


def test_import_transactions(session: Session, client: TestClient):
    # Arrange
    account_id = 1

    # Act
    response = client.post(f"/api/import/{account_id}", headers=ALICE_AUTH)
    transactions = session.exec(select(Transaction)).all()
    credits = session.exec(select(Credit)).all()
    payments = session.exec(select(Payment)).all()

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
    session.add(CreditTransaction(credit_id=credits[0].id, transaction_id=transactions[1].id, amount=1))
    session.commit()
    session.exec(select(CreditTransaction)).one()
    quiltt_mock.set_transactions(account.import_id, [])

    # Act 2
    response = client.post(f"/api/import/{account.id}", headers=ALICE_AUTH)
    transactions = session.exec(select(Transaction)).all()
    credits = session.exec(select(Credit)).all()
    payments = session.exec(select(Payment)).all()

    # Assert 2
    assert response.status_code == 204
    assert len(transactions) == 1
    assert len(credits) == 1
    assert len(payments) == 1

    with pytest.raises(NoResultFound):
        session.exec(select(CreditTransaction)).one()
