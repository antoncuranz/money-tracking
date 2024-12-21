from datetime import datetime
import json
import traceback
from decimal import Decimal

import requests
from peewee import DoesNotExist

from backend.config import Config
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
                type = self._get_type(tx)
                if type is Payment:
                    self._process_payment(account, tx)
                else:
                    self._process_transaction_or_credit(type, account, tx)
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

    def _process_payment(self, account, tx):
        args = self._make_transaction_args(tx, account.id)
        try:
            pending_payment = Payment.get(
                (Payment.account == account.id) & (Payment.status == Payment.Status.PENDING.value) & (Payment.amount_usd == args["amount_usd"])
            )
            print("Matching payment " + str(pending_payment.id))
            Payment.update(**args).where(Payment.id == pending_payment.id).execute()
            return
        except DoesNotExist:
            pass

        result, created = Payment.get_or_create(
            import_id=tx["remoteData"]["mx"]["transaction"]["id"],
            defaults=args
        )

        if created:
            self._send_notification("A Payment could not be matched")
            print("Error: Could not find pending Payment for {}.".format(json.dumps(tx)))

    def _process_transaction_or_credit(self, type, account, tx):
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
            "token": Config.pushover_token,
            "user": Config.pushover_user,
            "message": msg,
            "priority": priority
        })
