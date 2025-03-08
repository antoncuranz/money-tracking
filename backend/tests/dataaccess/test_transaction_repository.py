from core.dataaccess.transaction_repository import TransactionRepository
from models import Account, Transaction, User, BankAccount
from sqlmodel import Session
from tests.fixtures import *
import pytest

under_test = TransactionRepository()

@pytest.fixture(autouse=True)
def setup(session: Session):
    session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1), Account(**ACCOUNT_2)])


def test_get_pending_transaction_amount(session: Session):
    # Arrange
    account_id = 1
    session.add(Transaction.model_validate(TX_1, update={"status": 1, "ignore": True}))
    session.add(Transaction.model_validate(TX_2, update={"status": 1, "ignore": None}))
    session.add(Transaction.model_validate(TX_3, update={"status": 1, "ignore": None}))
    session.add(Transaction.model_validate(TX_4, update={"status": 1, "ignore": False}))
    expected_sum = TX_2["amount_usd"] + TX_3["amount_usd"]

    # Act
    result = under_test.get_pending_transaction_amount(session, account_id)

    # Assert
    assert result == expected_sum


def test_get_balance_pending(session: Session):
    # Arrange
    session.add(Transaction.model_validate(TX_1, update={"status": 1, "ignore": True}))
    session.add(Transaction.model_validate(TX_2, update={"status": 1, "ignore": None}))
    session.add(Transaction.model_validate(TX_3, update={"status": 1, "ignore": None}))
    session.add(Transaction.model_validate(TX_4, update={"status": 1, "ignore": False}))
    expected_sum = TX_2["amount_usd"] + TX_3["amount_usd"] + TX_4["amount_usd"]

    # Act
    result = under_test.get_balance_pending(session)

    # Assert
    assert result == expected_sum


def test_get_fees_and_risk_eur(session: Session):
    # Arrange
    session.add(Transaction.model_validate(TX_1, update={"status": 3, "fees_and_risk_eur": 1}))
    session.add(Transaction.model_validate(TX_2, update={"status": 3, "fees_and_risk_eur": 2}))
    session.add(Transaction.model_validate(TX_3, update={"status": 3, "fees_and_risk_eur": 3}))
    session.add(Transaction.model_validate(TX_4, update={"status": 3, "fees_and_risk_eur": 4}))
    expected_sum = 1 + 2 + 3 + 4

    # Act
    result = under_test.get_fees_and_risk_eur(session)

    # Assert
    assert result == expected_sum
    
def test_get_fees_and_risk_eur_no_rows(session: Session):
    # Arrange

    # Act
    result = under_test.get_fees_and_risk_eur(session)

    # Assert
    assert result == 0
