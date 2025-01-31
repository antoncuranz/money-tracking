import datetime
from typing import Annotated

import requests
from fastapi import Depends
from peewee import fn, DoesNotExist

from backend.config import config
from backend.data_export.facade import DataExportDep
from backend.data_import.business.quiltt_service import QuilttServiceDep
from backend.dates.facade import DatesDep
from backend.exchangerate.facade import ExchangeRateDep
from backend.models import Account, BankAccount, Payment, Transaction, Credit


class ImportService:
    def __init__(self, quiltt_service: QuilttServiceDep,
                 exchangerate: ExchangeRateDep,
                 dates: DatesDep,
                 data_export: DataExportDep):
        self.quiltt_service = quiltt_service
        self.exchangerate = exchangerate
        self.dates = dates
        self.data_export = data_export

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
        today = datetime.date.today()

        for account in Account.select():
            print("Importing transactions for Account {} {} ({})".format(account.institution, account.name, str(account.id)))

            try:
                self._import_account_transactions(account)
            except Exception as e:
                print("Error importing transactions: " + str(e))
                continue

            due_date = self.dates.get_next_due_date(account)
            last_statement_date = self.dates.get_statement_date_for_due_date(account, self.dates.get_last_due_date(account))
            statement_date = self.dates.get_statement_date_for_due_date(account, due_date)
            pending_payment = self._get_pending_payment(account, due_date)

            if statement_date + datetime.timedelta(days=1) < today < due_date and pending_payment is None:
                print("Creating pending payment")
                pending_payment = self._create_pending_payment(account, statement_date, last_statement_date, due_date)
                self._send_notification("Created pending Payment of {}. Please check amount_eur and exchange money.".format(pending_payment.amount_usd/100))

        for bank_account in BankAccount.select():
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

    def _import_account_transactions(self, account):
        self.quiltt_service.import_transactions(account)
        self.exchangerate.fetch_exchange_rates(account)
        if account.actual_id is not None:
            self.data_export.export_transactions(account)
            self.data_export.export_payments(account)

    def _get_pending_payment(self, account, due_date):
        try:
            return Payment.get((Payment.account == account.id) & (Payment.date == due_date) & (Payment.status == Payment.Status.PENDING.value))
        except DoesNotExist:
            return None

    def _create_pending_payment(self, account, statement_date, last_statement_date, due_date):
        amount_usd = Transaction.select(fn.SUM(Transaction.amount_usd)).where(
            (Transaction.account == account.id) & (Transaction.status == Transaction.Status.POSTED.value) & (Transaction.date <= statement_date)
        ).scalar() or 0
        amount_usd -= Credit.select(fn.SUM(Credit.amount_usd)).where(
            (Credit.account == account.id) & (Credit.date <= statement_date) & (Credit.date > last_statement_date)
        ).scalar() or 0
        return Payment.create(account_id=account.id, date=due_date, counterparty=account.institution, description="Upcoming Payment", amount_usd=amount_usd, status_enum=Payment.Status.PENDING)

    def _get_pending_payments_in_days(self, bank_account, days):
        today = datetime.date.today()
        end = today + datetime.timedelta(days=days)
        return Payment.select().join(Account).where(
            (Account.bank_account == bank_account.id) & (Payment.status == Payment.Status.PENDING.value) & (today <= Payment.date <= end)
        )

    def _send_notification(self, msg, priority=0):
        requests.post("https://api.pushover.net/1/messages.json", data = {
            "token": config.pushover_token,
            "user": config.pushover_user,
            "message": msg,
            "priority": priority
        })

ImportServiceDep = Annotated[ImportService, Depends()]