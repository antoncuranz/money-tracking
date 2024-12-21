from backend.data_export.actual_service import ActualService
from backend.core.service.exchange_service import ExchangeService
from backend.data_import.quiltt_service import QuilttService
from flask_injector import inject
from backend.models import *


class ImportService:

    @inject
    def __init__(self, quiltt_service: QuilttService, exchange_service: ExchangeService, actual_service: ActualService):
        self.quiltt_service = quiltt_service
        self.exchange_service = exchange_service
        self.actual_service = actual_service

    def import_transactions(self, user, account_id):
        """
        Raises
        ------
        DoesNotExist
            If an account with the given `account_id` does not exist or does not belong to the given `user`.
        """
        
        account = Account.get((Account.user == user.id) & (Account.id == account_id))
        self._import_account_transactions(account)

    def import_transactions_all_accounts(self):
        for account in Account.select():
            print("Importing transactions for Account {} {} ({})".format(account.institution, account.name, str(account.id)))

            try:
                self._import_account_transactions(account)
            except Exception as e:
                print("Error importing transactions: " + str(e))
                continue

        for bank_account in BankAccount.select():
            print("Importing balances for BankAccount " + str(bank_account.id))

            try:
                self.quiltt_service.update_bank_account_balance(bank_account)
            except Exception as e:
                print("Error importing balances: " + str(e))
                continue

    def _import_account_transactions(self, account):
        self.quiltt_service.import_transactions(account)
        self.exchange_service.fetch_exchange_rates(account)
        if account.actual_id is not None:
            self.actual_service.export_transactions(account)
            self.actual_service.export_payments(account)
