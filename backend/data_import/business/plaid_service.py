import json
import traceback
from decimal import Decimal
from typing import Annotated

import requests
from fastapi import Depends
from sqlmodel import Session

from backend.config import config
from backend.data_import.dataaccess.dataimport_repository import DataImportRepository
from backend.models import Transaction, Account

import plaid
from plaid.api import plaid_api
from plaid.model.transactions_sync_request import TransactionsSyncRequest


class PlaidService:
    def __init__(self, repository: Annotated[DataImportRepository, Depends()]):
        self.repository = repository
        
        configuration = plaid.Configuration(
            host=plaid.Environment.Production if config.plaid_environment == "production" else plaid.Environment.Sandbox,
            api_key={
                "clientId": config.plaid_client_id,
                "secret": config.plaid_secret,
                "plaidVersion": "2020-09-14"
            }
        )
        self.client = plaid_api.PlaidApi(plaid.ApiClient(configuration))

    def update_bank_account_balance(self, session: Session, bank_account):
        # accounts, _ = self._plaid_request(bank_account.plaid_token)
        pass
        
        # new_balance = self.adapter.get_account_balance(bank_account.import_id, self._get_token())
        # bank_account.balance = int(new_balance * 100)
        # session.add(bank_account)
    
    def _plaid_request(self, access_token: str):
        request = TransactionsSyncRequest(access_token=access_token)
        response = self.client.transactions_sync(request)
        accounts = response["accounts"]
        transactions = response["added"]

        # the transactions in the response are paginated, so make multiple calls while incrementing the cursor to
        # retrieve all transactions
        while response["has_more"]:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=response["next_cursor"]
            )
            response = self.client.transactions_sync(request)
            transactions += response["added"]

        return accounts, transactions

    def import_transactions(self, session: Session, account: Account):
        _, transactions = self._plaid_request(config.plaid_access_token)  # TODO: access_token = account.plaid_token
        # FIXME: might contain transactions of multiple accounts
        
        for tx in transactions:
            if tx["pending"]:
                print("Skipping pending transaction")
                continue
            try:
                if tx["amount"] < 0:
                    payment_strings = ["AUTOPAY PAYMENT", "AUTOPAY PYMT", "MOBILE PAYMENT", "MOBILE PYMT"]
                    if any(payment_string in tx["name"] for payment_string in payment_strings):
                        self._process_payment(session, account, tx)
                    else:
                        self._process_credit(session, account, tx)
                else:
                    self._process_transaction(session, account, tx)
            except:
                print("Error processing plaid transaction: " + json.dumps(tx))
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

        import_id = tx["transaction_id"]
        args = self._make_transaction_args(tx, account.id)
        result, created = self.repository.get_or_create_payment(session, import_id, args)

        if created:
            self._send_notification("A Payment could not be matched")
            print("Error: Could not find pending Payment for {}.".format(self._print_tx(tx)))
            session.commit()
    
    def _print_tx(self, plaid_tx):
        return "(id: {}; date: {}; name: {}; amount: {})".format(
            plaid_tx["transaction_id"], plaid_tx["date"], plaid_tx["name"], plaid_tx["amount"]
        )
            
    def _process_transaction(self, session: Session, account: Account, tx):
        import_id = tx["transaction_id"]
        args = self._make_transaction_args(tx, account.id)
        self.repository.get_or_create_transaction(session, import_id, args)

    def _process_credit(self, session: Session, account: Account, tx):
        import_id = tx["transaction_id"]
        args = self._make_transaction_args(tx, account.id)
        self.repository.get_or_create_credit(session, import_id, args)

    def _make_transaction_args(self, tx, account_id):
        counterparty = next((cp["name"] for cp in tx["counterparties"] if "HIGH" in cp["confidence_level"]), None)
        return {
            "account_id": account_id,
            "import_id": tx["transaction_id"],
            "date": tx["date"],
            "counterparty": counterparty or tx["merchant_name"] or tx["name"],
            "description": tx["name"],
            "amount_usd": abs(int(Decimal(tx["amount"] * 100).quantize(1))),
            "status": Transaction.Status.POSTED.value
        }

    def _send_notification(self, msg, priority=0):
        requests.post("https://api.pushover.net/1/messages.json", data = {
            "token": config.pushover_token,
            "user": config.pushover_user,
            "message": msg,
            "priority": priority
        })
        
