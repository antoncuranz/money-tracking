import datetime
from typing import Annotated

import requests
from fastapi import Depends, HTTPException

from backend.config import config
from backend.data_export.facade import DataExportFacade
from backend.data_import.business.quiltt_service import QuilttService
from backend.data_import.dataaccess.dataimport_repository import DataImportRepository
from backend.dates.facade import DatesFacade
from backend.exchangerate.facade import ExchangeRateFacade
from backend.models import Account, User, BankAccount


class ImportService:
    def __init__(self, quiltt_service: Annotated[QuilttService, Depends()],
                 repository: Annotated[DataImportRepository, Depends()],
                 exchangerate: Annotated[ExchangeRateFacade, Depends()],
                 dates: Annotated[DatesFacade, Depends()],
                 data_export: Annotated[DataExportFacade, Depends()]):
        self.quiltt_service = quiltt_service
        self.repository = repository
        self.exchangerate = exchangerate
        self.dates = dates
        self.data_export = data_export

    def import_transactions(self, user: User, account_id: int):
        account = self.repository.get_account(user, account_id)
        if not account:
            raise HTTPException(status_code=404)
        
        self._import_account_transactions(account)

    def import_transactions_all_accounts(self):
        today = datetime.date.today()

        for account in self.repository.get_all_accounts():
            print("Importing transactions for Account {} {} ({})".format(account.institution, account.name, str(account.id)))

            try:
                self._import_account_transactions(account)
            except Exception as e:
                print("Error importing transactions: " + str(e))
                continue

            due_date = self.dates.get_next_due_date(account)
            last_statement_date = self.dates.get_statement_date_for_due_date(account, self.dates.get_last_due_date(account))
            statement_date = self.dates.get_statement_date_for_due_date(account, due_date)
            pending_payment = self.repository.get_pending_payment(account, due_date)

            if statement_date + datetime.timedelta(days=1) < today < due_date and pending_payment is None:
                print("Creating pending payment")
                pending_payment = self.repository.create_pending_payment(account, statement_date, last_statement_date, due_date)
                self._send_notification("Created pending Payment of {}. Please check amount_eur and exchange money.".format(pending_payment.amount_usd/100))

        for bank_account in self.repository.get_all_bank_accounts():
            print("Importing balances for BankAccount " + str(bank_account.id))

            try:
                self.quiltt_service.update_bank_account_balance(bank_account)
            except Exception as e:
                print("Error importing balances: " + str(e))
                continue

            pending_payment_sum = sum(p.amount_usd for p in self._get_pending_payments_in_days(bank_account, 3))
            print("Pending sum: " + str(pending_payment_sum))
            if pending_payment_sum > bank_account.balance:
                self._send_notification("Betrag {} in Kürze fällig. Bankkonto {} nicht ausreichend gedeckt.".format(pending_payment_sum/100, bank_account.name))

        # pending_exchanges = Exchange.select().where(Exchange.import_id.is_null())
        # if pending_exchanges:
            # match_pending_exchanges_in_main_acct()  # TODO: send notification once exchange posted:
            # Exchange posted. Please transfer X to bank account A and Y to bank account B

    def _import_account_transactions(self, account: Account):
        self.quiltt_service.import_transactions(account)
        self.exchangerate.fetch_exchange_rates(account)
        if account.actual_id is not None:
            self.data_export.export_transactions(account.user, account.id)
            self.data_export.export_payments(account.user, account.id)

    def _get_pending_payments_in_days(self, bank_account: BankAccount, days: int):
        today = datetime.date.today()
        end = today + datetime.timedelta(days=days)
        return self.repository.get_pending_payments_between(bank_account.id, today, end)

    def _send_notification(self, msg: str, priority=0):
        requests.post("https://api.pushover.net/1/messages.json", data = {
            "token": config.pushover_token,
            "user": config.pushover_user,
            "message": msg,
            "priority": priority
        })
