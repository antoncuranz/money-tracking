from datetime import date, datetime, time, timedelta
from typing import Annotated

import requests
from fastapi import Depends, HTTPException
from sqlmodel import Session

from config import config
from data_export.facade import DataExportFacade
from data_import.business.abstract_importer import AbstractImporter
from data_import.business.plaid_importer import PlaidImporter
from data_import.dataaccess.dataimport_repository import DataImportRepository
from dates.facade import DatesFacade
from exchangerate.facade import ExchangeRateFacade
from models import Account, User, BankAccount


class ImportService:
    def __init__(self, importer: Annotated[AbstractImporter, Depends(PlaidImporter)],
                 repository: Annotated[DataImportRepository, Depends()],
                 exchangerate: Annotated[ExchangeRateFacade, Depends()],
                 dates: Annotated[DatesFacade, Depends()],
                 data_export: Annotated[DataExportFacade, Depends()]):
        self.importer = importer
        self.repository = repository
        self.exchangerate = exchangerate
        self.dates = dates
        self.data_export = data_export

    def import_transactions(self, session: Session, user: User, account_id: int):
        account = self.repository.get_account(session, user, account_id)
        if not account:
            raise HTTPException(status_code=404)
        
        self._import_account_transactions(session, account)
        session.commit()

    def import_transactions_all_accounts(self, session: Session):
        today = date.today()

        for account in self.repository.get_all_accounts(session):
            print("Importing transactions for Account {} {} ({})".format(account.institution, account.name, str(account.id)))

            try:
                self._import_account_transactions(session, account)
            except Exception as e:
                err_msg = "Error importing transactions: " + str(e)
                print(err_msg)
                self._send_notification(err_msg)
                continue

            due_date = self.dates.get_next_due_date(account)
            last_statement_date = self.dates.get_statement_date_for_due_date(account, self.dates.get_last_due_date(account))
            statement_date = self.dates.get_statement_date_for_due_date(account, due_date)
            pending_payment = self.repository.get_pending_payment(session, account.id, due_date)
            last_successful_update = account.plaid_account.last_successful_update

            if pending_payment is None and last_successful_update > datetime.combine(statement_date, time(0, 0)) + timedelta(days=1) and today < due_date:
                print("Creating pending payment (statement_date: {}; last_update: {})".format(statement_date, last_successful_update))
                pending_payment = self.repository.create_pending_payment(session, account, statement_date, last_statement_date, due_date)
                self._send_notification("Created pending Payment of {}. Please check amount_eur and exchange money.".format(pending_payment.amount_usd/100))

        for bank_account in self.repository.get_all_bank_accounts(session):
            print("Importing balances for BankAccount " + str(bank_account.id))

            try:
                self.importer.update_bank_account_balance(session, bank_account)
            except Exception as e:
                print("Error importing balances: " + str(e))
                continue

            pending_payment_sum = sum(p.amount_usd for p in self._get_pending_payments_in_days(session, bank_account, 3))
            print("Pending sum: " + str(pending_payment_sum))
            if pending_payment_sum > bank_account.balance:
                self._send_notification("Betrag {} in Kürze fällig. Bankkonto {} nicht ausreichend gedeckt.".format(pending_payment_sum/100, bank_account.name))
        
        session.commit()

        # pending_exchanges = Exchange.select().where(Exchange.import_id.is_null())
        # if pending_exchanges:
            # match_pending_exchanges_in_main_acct()  # TODO: send notification once exchange posted:
            # Exchange posted. Please transfer X to bank account A and Y to bank account B

    def _import_account_transactions(self, session: Session, account: Account):
        self.importer.import_transactions(session, account)
        self.exchangerate.fetch_exchange_rates(session, account)
        if account.actual_id is not None:
            self.data_export.export_transactions(session, account.user, account.id)

    def _get_pending_payments_in_days(self, session: Session, bank_account: BankAccount, days: int):
        today = date.today()
        end = today + timedelta(days=days)
        return self.repository.get_pending_payments_between(session, bank_account.id, today, end)

    def _send_notification(self, msg: str, priority=0):
        requests.post("https://api.pushover.net/1/messages.json", data = {
            "token": config.pushover_token,
            "user": config.pushover_user,
            "message": msg,
            "priority": priority
        })
