import json
import traceback
from decimal import Decimal
from typing import Annotated

import plaid
from fastapi import Depends
from plaid.api import plaid_api
from sqlmodel import Session

from config import config
from data_import.business.abstract_importer import AbstractImporter
from data_import.business.plaid_service import PlaidService
from data_import.dataaccess.dataimport_repository import DataImportRepository
from models import Transaction, Account


class PlaidImporter(AbstractImporter):
    def __init__(self, repository: Annotated[DataImportRepository, Depends()],
                 plaid_service: Annotated[PlaidService, Depends()]):
        super().__init__(repository)
        self.plaid_service = plaid_service
        configuration = plaid.Configuration(
            host=plaid.Environment.Production if config.plaid_environment == "production" else plaid.Environment.Sandbox,
            api_key={"clientId": config.plaid_client_id, "secret": config.plaid_secret, "plaidVersion": "2020-09-14"}
        )
        self.client = plaid_api.PlaidApi(plaid.ApiClient(configuration))

    def update_bank_account_balance(self, session: Session, bank_account):
        # TODO
        # accounts, _ = self._plaid_request(bank_account.plaid_token)
        pass
        # new_balance = self.adapter.get_account_balance(bank_account.import_id, self._get_token())
        # bank_account.balance = int(new_balance * 100)
        # session.add(bank_account)
    
    def import_transactions(self, session: Session, account: Account):
        _, transactions = self.plaid_service.sync_transactions(config.plaid_access_token)  # TODO: access_token = account.plaid_token
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
