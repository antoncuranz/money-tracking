import datetime

from backend.data_import.dataaccess.dataimport_repository import DataImportRepository
from backend.models import Account, Transaction, User, Payment, Credit, BankAccount
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound
from backend.tests.fixtures import *
import pytest

under_test = DataImportRepository()


@pytest.fixture(autouse=True)
def setup(session: Session):
    session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1), Account(**ACCOUNT_2)])


def test_get_account(session: Session):
    # Arrange
    account_id = 1
    user = session.exec(select(User).where(User.id == 1)).one()

    # Act
    account = under_test.get_account(session, user, account_id)

    # Assert
    assert account.id == account_id


def test_get_pending_payment(session: Session):
    # Arrange
    account_id = 1
    date = datetime.date.today()
    amount_usd = 123

    session.add(Payment(account_id=account_id, date=date, counterparty="cp", description="desc", amount_usd=amount_usd, status=1))

    # Act
    result = under_test.get_pending_payment(session, account_id, date, amount_usd)

    # Assert
    assert result is not None


def test_get_pending_payment_no_amount(session: Session):
    # Arrange
    account_id = 1
    date = datetime.date.today()
    amount_usd = 123

    session.add(Payment(account_id=account_id, date=date, counterparty="cp", description="desc", amount_usd=amount_usd, status=1))

    # Act
    result = under_test.get_pending_payment(session, account_id, date)

    # Assert
    assert result is not None


def test_create_pending_payment(session: Session):
    # Arrange
    account = session.exec(select(Account).where(Account.id == 1)).one()
    last_statement_date = datetime.date(2024, 1, 1)
    statement_date = datetime.date(2024, 1, 3)
    due_date = datetime.date(2024, 1, 20)

    session.add_all([Transaction(**TX_1), Transaction(**TX_2), Transaction(**TX_3), Transaction(**TX_4)])
    session.add(Credit.model_validate(CREDIT_1, update={"date": "2024-01-02", "amount_usd": 100}))
    expected_amount_usd = 552 + 2193 - 100  # tx2 + tx3 - credit

    # Act
    created = under_test.create_pending_payment(session, account, statement_date, last_statement_date, due_date)
    session.commit()
    persisted = session.exec(select(Payment).where(Payment.id == created.id)).one()

    # Assert
    assert persisted is not None
    assert persisted.status == Payment.Status.PENDING.value
    assert persisted.date == due_date
    assert persisted.amount_usd == expected_amount_usd


def test_create_pending_payment_no_rows(session: Session):
    # Arrange
    account = session.exec(select(Account).where(Account.id == 1)).one()
    statement_date = datetime.date.today()
    last_statement_date = datetime.date.today() + datetime.timedelta(days=3)
    due_date = datetime.date.today()

    # Act
    created = under_test.create_pending_payment(session, account, statement_date, last_statement_date, due_date)
    session.commit()
    persisted = session.exec(select(Payment).where(Payment.id == created.id)).one()

    # Assert
    assert persisted is not None
    assert persisted.status == Payment.Status.PENDING.value
    assert persisted.date == due_date
    assert persisted.amount_usd == 0


def test_get_pending_payments_between(session: Session):
    # Arrange
    date_from = datetime.date(2024, 1, 2)
    date_to = datetime.date(2024, 1, 3)
    bank_account_id = 1

    session.add(Payment(account_id=1, date=datetime.date(2024, 1, 1), counterparty="cp", description="desc", amount_usd=123, status=1))
    session.add(Payment(account_id=1, date=datetime.date(2024, 1, 2), counterparty="cp", description="desc", amount_usd=123, status=1))
    session.add(Payment(account_id=1, date=datetime.date(2024, 1, 3), counterparty="cp", description="desc", amount_usd=123, status=1))
    session.add(Payment(account_id=1, date=datetime.date(2024, 1, 4), counterparty="cp", description="desc", amount_usd=123, status=1))
    session.commit()

    # Act
    payments = under_test.get_pending_payments_between(session, bank_account_id, date_from, date_to)

    # Assert
    assert len(payments) == 2
    assert [payment.id for payment in payments] == [2, 3]


@pytest.mark.parametrize("model_class, args, get_or_create_func", [
    (Transaction, TX_1, under_test.get_or_create_transaction),
    (Credit, CREDIT_1, under_test.get_or_create_credit),
    (Payment, PAYMENT_1, under_test.get_or_create_payment)
])
def test_get_or_create(session: Session, model_class, args, get_or_create_func):
    # Arrange
    with pytest.raises(NoResultFound):
        session.exec(select(model_class).where(model_class.import_id == args["import_id"])).one()

    # Act
    model, created = get_or_create_func(session, args["import_id"], args)
    session.commit()

    # Assert
    assert created is True
    session.exec(select(model_class).where(model_class.import_id == args["import_id"])).one()


@pytest.mark.parametrize("model_class, args, get_or_create_func", [
    (Transaction, TX_1, under_test.get_or_create_transaction),
    (Credit, CREDIT_1, under_test.get_or_create_credit),
    (Payment, PAYMENT_1, under_test.get_or_create_payment)
])
def test_get_or_create_payment_existing(session: Session, model_class, args, get_or_create_func):
    # Arrange
    session.add(model_class(**args))
    session.exec(select(model_class).where(model_class.import_id == args["import_id"])).one()

    # Act
    model, created = get_or_create_func(session, args["import_id"], args)

    # Assert
    assert created is False
    session.exec(select(model_class).where(model_class.import_id == args["import_id"])).one()
