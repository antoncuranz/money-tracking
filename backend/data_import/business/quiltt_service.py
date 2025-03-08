import json
import traceback
from datetime import datetime
from decimal import Decimal
from typing import Annotated

import requests
from fastapi import Depends
from sqlmodel import Session

from config import config
from data_import.adapter.quiltt_client import IQuilttClient, QuilttClient
from data_import.dataaccess.dataimport_repository import DataImportRepository
from models import Transaction, Account


class QuilttService:
    def __init__(self, adapter: Annotated[IQuilttClient, Depends(QuilttClient)],
                 repository: Annotated[DataImportRepository, Depends()]):
        self.adapter = adapter
        self.repository = repository
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
                print("Error processing quiltt_tx: " + json.dumps(tx))
                traceback.print_exc()

    def _process_payment(self, session: Session, account: Account, tx):
        args = self._make_transaction_args(tx, account.id)
        
        pending_payment = self.repository.get_pending_payment(session, account.id, args["date"], args["amount_usd"])
        if pending_payment:
            print("Matching payment " + str(pending_payment.id))
            pending_payment = pending_payment.model_copy(update=args)
            session.add(pending_payment)
            session.commit()
            return

        import_id = tx["remoteData"]["mx"]["transaction"]["id"]
        args = self._make_transaction_args(tx, account.id)
        result, created = self.repository.get_or_create_payment(session, import_id, args)

        if created:
            self._send_notification("A Payment could not be matched")
            print("Error: Could not find pending Payment for {}.".format(json.dumps(tx)))
            session.commit()
            
    def _process_transaction(self, session: Session, account: Account, tx):
        import_id = tx["remoteData"]["mx"]["transaction"]["id"]
        args = self._make_transaction_args(tx, account.id)
        self.repository.get_or_create_transaction(session, import_id, args)

    def _process_credit(self, session: Session, account: Account, tx):
        import_id = tx["remoteData"]["mx"]["transaction"]["id"]
        args = self._make_transaction_args(tx, account.id)
        self.repository.get_or_create_credit(session, import_id, args)

    def _make_transaction_args(self, tx, account_id):
        args = { # always available args
            "account_id": account_id,
            "import_id": tx["remoteData"]["mx"]["transaction"]["id"],
            "date": tx["date"],
            "counterparty": tx["description"],
            "description": tx["remoteData"]["mx"]["transaction"]["response"]["originalDescription"],
            "amount_usd": abs(int(Decimal(tx["amount"] * 100).quantize(1))),
            "status": Transaction.Status.POSTED.value
        }

        return args

    def _get_token(self):
        if self.token is None or (self.token_expires is not None and datetime.now() > self.token_expires):
            print("Retrieving Quiltt Session Token...")
            self.token, self.token_expires = self.adapter.retrieve_session_token()
            print(self.token)

        return self.token

    def _send_notification(self, msg, priority=0):
        requests.post("https://api.pushover.net/1/messages.json", data = {
            "token": config.pushover_token,
            "user": config.pushover_user,
            "message": msg,
            "priority": priority
        })
        
