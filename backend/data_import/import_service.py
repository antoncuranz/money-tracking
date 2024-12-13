from backend.data_export.actual_service import ActualService
from backend.core.service.exchange_service import ExchangeService
from backend.data_import.teller_client import TellerMfaRequired
from backend.data_import.teller_service import TellerService
from flask_injector import inject
from backend.models import *


class ImportService:

    @inject
    def __init__(self, teller_service: TellerService, exchange_service: ExchangeService, actual_service: ActualService):
        self.teller_service = teller_service
        self.exchange_service = exchange_service
        self.actual_service = actual_service

    def import_transactions(self, user, account_id, access_token=None, enrollment=None):
        """
        Raises
        ------
        DoesNotExist
            If an account with the given `account_id` does not exist or does not belong to the given `user`.
        TellerMfaRequired
            If teller interaction is required.
        """
        
        account = Account.get((Account.user == user.id) & (Account.id == account_id))

        if access_token is not None:
            account.teller_access_token = access_token
            account.save()

        if enrollment is not None:
            account.teller_enrollment_id = enrollment
            account.save()

        self.teller_service.import_transactions(account)
        self.exchange_service.fetch_exchange_rates(account)
        self.actual_service.export_transactions(account)

    def import_transactions_all_accounts(self):
        for account in Account.select():
            print("Importing transactions for {} {} ({})".format(account.institution, account.name, str(account.id)))

            try:
                self.teller_service.import_transactions(account)
            except TellerMfaRequired:
                print("Teller interaction required")
                continue

            try:
                self.exchange_service.fetch_exchange_rates(account)
            except:
                print("Error fetching exchange rates")

            try:
                self.actual_service.export_transactions(account)
                self.actual_service.export_payments(account)
            except:
                print("Error importing transactions into Actual")
