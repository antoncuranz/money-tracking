import json
import traceback
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from data_import.adapter.quiltt_client import IQuilttClient, QuilttClient
from data_import.business.abstract_importer import AbstractImporter
from data_import.dataaccess.dataimport_repository import DataImportRepository
from models import Transaction, Account


class QuilttImporter(AbstractImporter):
    def __init__(self, adapter: Annotated[IQuilttClient, Depends(QuilttClient)],
                 repository: Annotated[DataImportRepository, Depends()]):
        super().__init__(repository)
        self.adapter = adapter
        self.token = None
        self.token_expires = None

    def update_bank_account_balance(self, session: Session, bank_account):
        new_balance = self.adapter.get_account_balance(bank_account.import_id, self._get_token())
        bank_account.balance = int(new_balance * 100)
        session.add(bank_account)

    def import_transactions(self, session: Session, account: Account):
        quiltt_response = self.adapter.get_account_transactions(account.import_id, self._get_token())

        for tx in quiltt_response:
            try:
                if tx["amount"] > 0:
                    original_description = tx["remoteData"]["mx"]["transaction"]["response"]["originalDescription"]
                    payment_strings = ["AUTOPAY PAYMENT", "AUTOPAY PYMT", "MOBILE PAYMENT", "MOBILE PYMT"]
                    
                    if any(payment_string in original_description for payment_string in payment_strings):
                        self._process_payment(session, account, tx)
                    else:
                        self._process_credit(session, account, tx)
                else:
                    self._process_transaction(session, account, tx)
            except:
                print("Error processing quiltt_tx: " + self._print_tx(tx))
                traceback.print_exc()

    def _make_transaction_args(self, tx, account_id):
        return {
            "account_id": account_id,
            "import_id": tx["remoteData"]["mx"]["transaction"]["id"],
            "date": tx["date"],
            "counterparty": tx["description"],
            "description": tx["remoteData"]["mx"]["transaction"]["response"]["originalDescription"],
            "amount_usd": abs(int(Decimal(tx["amount"] * 100).quantize(1))),
            "status": Transaction.Status.POSTED.value
        }

    def _get_token(self):
        if self.token is None or (self.token_expires is not None and datetime.now() > self.token_expires):
            print("Retrieving Quiltt Session Token...")
            self.token, self.token_expires = self.adapter.retrieve_session_token()
            print(self.token)

        return self.token
