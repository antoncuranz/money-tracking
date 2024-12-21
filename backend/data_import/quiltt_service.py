from datetime import datetime
import json
import traceback
from decimal import Decimal

from backend.data_import.quiltt_client import IQuilttClient
from backend.models import Transaction, Credit, Payment
from flask_injector import inject


class QuilttService:

    @inject
    def __init__(self, adapter: IQuilttClient):
        self.adapter = adapter
        self.token = None
        self.token_expires = None

    def update_bank_account_balance(self, bank_account):
        new_balance = self.adapter.get_account_balance(bank_account.import_id, self._get_token())
        bank_account.balance = int(new_balance * 100)
        bank_account.save()

    def import_transactions(self, account):
        quiltt_response = self.adapter.get_account_transactions(account.import_id, self._get_token())

        for tx in quiltt_response:
            try:
                self._process_transaction(self._get_type(tx), account, tx)
            except:
                print("Error processing quiltt_tx: " + json.dumps(tx))
                traceback.print_exc()

    def _get_type(self, tx):
        if tx["amount"] > 0:
            original_description = tx["remoteData"]["mx"]["transaction"]["response"]["originalDescription"]
            payment_strings = ["AUTOPAY PAYMENT", "AUTOPAY PYMT", "MOBILE PAYMENT", "MOBILE PYMT"]
            if any(payment_string in original_description for payment_string in payment_strings):
                return Payment
            else:
                return Credit
        else:
            return Transaction

    def _process_transaction(self, type, account, tx):
        type.get_or_create(
            import_id=tx["remoteData"]["mx"]["transaction"]["id"],
            defaults=self._make_transaction_args(tx, account.id)
        )

    def _make_transaction_args(self, tx, account_id):
        args = { # always available args
            "account_id": account_id,
            "import_id": tx["remoteData"]["mx"]["transaction"]["id"],
            "date": tx["date"],
            "counterparty": tx["description"],
            "description": tx["remoteData"]["mx"]["transaction"]["response"]["originalDescription"],
            "category": "unknown",
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
