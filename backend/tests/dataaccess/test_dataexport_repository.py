from backend.data_export.dataaccess.dataexport_repository import DataExportRepository
from backend.models import Account, Transaction, User, Payment, BankAccount
from sqlmodel import Session, select
from backend.tests.fixtures import *
import pytest

under_test = DataExportRepository()

@pytest.fixture(autouse=True)
def setup(session: Session):
    session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1), Account(**ACCOUNT_2)])

def test_get_unexported_transactions(session: Session):
    # Arrange
    account_id = 1
    session.add(Transaction.model_validate(TX_1, update={"actual_id": "something"}))
    session.add_all([Transaction(**TX_2), Transaction(**TX_3), Transaction(**TX_4), Transaction(**TX_5), Transaction(**TX_6)])
    session.commit()

    # Act
    result = under_test.get_unexported_transactions(session, account_id)
    
    # Assert
    assert len(result) == 3
    assert [tx.id for tx in result] == [2, 3, 6]

def test_get_updatable_transactions(session: Session):
    # Arrange
    account_id = 1
    session.add(Transaction.model_validate(TX_1, update={"actual_id": "something"}))
    session.add(Transaction.model_validate(TX_2, update={"actual_id": "something", "amount_eur": None}))
    session.add_all([Transaction(**TX_3), Transaction(**TX_4), Transaction(**TX_5), Transaction(**TX_6)])

    # Act
    result = under_test.get_updatable_transactions(session, account_id)

    # Assert
    assert len(result) == 1
    assert [tx.id for tx in result] == [1]

def test_get_unexported_payments(session: Session):
    # Arrange
    account_id = 1
    session.add(Payment.model_validate(PAYMENT_1, update={"status": 3, "amount_eur": 123, "actual_id": "something"}))
    session.add(Payment.model_validate(PAYMENT_2, update={"status": 3, "amount_eur": 123, "actual_id": None}))
    session.add(Payment.model_validate(PAYMENT_3, update={"status": 3, "amount_eur": None, "actual_id": None}))

    # Act
    result = under_test.get_unexported_payments(session, account_id)

    # Assert
    assert len(result) == 1
    assert [payment.id for payment in result] == [2]
    
def test_get_unexported_payments_only_processed(session: Session):
    # Arrange
    account_id = 1
    session.add(Payment.model_validate(PAYMENT_1, update={"status": 1, "amount_eur": 123, "actual_id": None}))
    session.add(Payment.model_validate(PAYMENT_2, update={"status": 2, "amount_eur": 123, "actual_id": None}))
    session.add(Payment.model_validate(PAYMENT_3, update={"status": 3, "amount_eur": 123, "actual_id": None}))

    # Act
    result = under_test.get_unexported_payments(session, account_id)

    # Assert
    assert len(result) == 1
    assert [payment.id for payment in result] == [3]

def test_get_account(session: Session):
    # Arrange
    account_id = 1
    user = session.exec(select(User).where(User.id == 1)).one()
    
    # Act
    account = under_test.get_account(session, user, account_id)
    
    # Assert
    assert account.id == account_id
