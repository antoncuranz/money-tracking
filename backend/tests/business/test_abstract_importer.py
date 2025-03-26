import copy

import pytest
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound

from data_import.business.abstract_importer import AbstractImporter
from data_import.dataaccess.dataimport_repository import DataImportRepository
from models import User, Account, BankAccount, Payment
from tests.fixtures import *


@pytest.fixture(autouse=True)
def setup(session: Session):
    session.add_all([User(**ALICE_USER), Account(**ACCOUNT_1), BankAccount(**BANK_ACCOUNT_1)])


class AbstractImporterImpl(AbstractImporter):
    
    def __init__(self, tx_args_override=None):
        super().__init__(DataImportRepository())
        self.tx_args_override = tx_args_override
    
    def set_tx_args_override(self, tx_args_override):
        self.tx_args_override = tx_args_override
    
    def update_bank_account_balance(self, session: Session, bank_account: BankAccount):
        pass

    def import_transactions(self, session: Session, account: Account):
        pass

    def _make_transaction_args(self, tx, account_id):
        return self.tx_args_override
    
    def _print_tx(self, plaid_tx):
        pass


def test_payment_processing(session: Session):
    # Arrange (general)
    with pytest.raises(NoResultFound):
        session.exec(select(Payment)).one()

    account = session.exec(select(Account)).one()
    
    # Arrange 1
    payment = copy.copy(PAYMENT_1)
    payment["status"] = Payment.Status.PENDING.value
    under_test = AbstractImporterImpl(payment)
    # Act & Assert 1
    under_test._process_payment(session, account, None)
    persisted = session.exec(select(Payment)).one()
    assert persisted.status == Payment.Status.PENDING.value
    
    # Arrange 2
    under_test.set_tx_args_override(PAYMENT_1)
    # Act & Assert 2
    under_test._process_payment(session, account, None)
    persisted = session.exec(select(Payment)).one()
    assert persisted.status == Payment.Status.POSTED.value
