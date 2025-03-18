import datetime

import pytest
from plaid.model.transaction import Transaction as PlaidTransaction
from sqlmodel import Session, select

from data_import.business.plaid_importer import PlaidImporter
from data_import.dataaccess.dataimport_repository import DataImportRepository
from models import User, Account, PlaidAccount, PlaidConnection, BankAccount, Transaction
from tests.fixtures import *


@pytest.fixture(autouse=True)
def setup(session: Session):
    account = Account(**ACCOUNT_1)
    account.plaid_account_id = 1
    session.add_all([User(**ALICE_USER), account, BankAccount(**BANK_ACCOUNT_1), PlaidConnection(**PLAID_CONNECTION_1), PlaidAccount(**PLAID_ACCOUNT_1)])


def _create_plaid_tx(account_id: str, amount: float, transaction_id: str, date: datetime.date, pending: bool):
    return PlaidTransaction(account_id=account_id, amount=amount, iso_currency_code=None, unofficial_currency_code=None,
                category=None, category_id=None, date=date, location=None, name="Description", merchant_name="Merchant Name",
                payment_meta=None, pending=pending, pending_transaction_id=None, account_owner=None,
                transaction_id=transaction_id, authorized_date=None, authorized_datetime=None, datetime=None,
                payment_channel=None, transaction_code=None, counterparties=[], _check_type=False)


def test_import_transactions(mocker, session: Session):
    # Arrange
    account = session.exec(select(Account).where(User.id == 1)).one()
    assert len(session.exec(select(Transaction)).all()) == 0

    added = [
        _create_plaid_tx(account_id="plaid-account-1", amount=12.34, date=datetime.date(2025, 1, 3), pending=True, transaction_id="plaid-tx-3"),
        _create_plaid_tx(account_id="plaid-account-1", amount=43.21, date=datetime.date(2025, 1, 2), pending=False, transaction_id="plaid-tx-2"),
        _create_plaid_tx(account_id="plaid-account-1", amount=12.34, date=datetime.date(2025, 1, 1), pending=False, transaction_id="plaid-tx-1")
        # create_plaid_tx(account_id="plaid-account-2", amount=12.34, date=datetime.date(2025, 1, 2), pending=False, transaction_id="plaid-tx-4")
    ]
    modified = []
    removed = [
        # RemovedTransaction()
    ]
    next_cursor = "cursor-1000"

    plaid_service_mock = mocker.Mock()
    plaid_service_mock.sync_transactions.return_value = added, modified, removed, next_cursor
    under_test = PlaidImporter(DataImportRepository(), plaid_service_mock)

    
    # Act
    under_test.import_transactions(session, account)

    # Assert
    transactions = session.exec(select(Transaction)).all()
    assert len(transactions) == 2
    assert transactions[0].amount_usd == 1234
    assert transactions[1].amount_usd == 4321
