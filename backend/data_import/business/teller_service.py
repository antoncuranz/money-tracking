import json
import re
import traceback

from typing import Annotated
from fastapi import Depends

from backend.data_import.adapter.teller_client import ITellerClient, TellerMfaRequired, TellerClient
from backend.models import Transaction, Credit, Payment


class TellerService:
    def __init__(self, teller: Annotated[ITellerClient, Depends(TellerClient)]):
        self.teller = teller

    def import_transactions(self, account):
        if account.teller_enrollment_id is None or account.teller_access_token is None:
            raise TellerMfaRequired()

        if account.teller_id is None:
            teller_account = self.teller.list_accounts(account)[0]
            account.teller_id = teller_account["id"]
            account.name = teller_account["name"]
            account.institution = teller_account["institution"]["name"]
            account.save()

        teller_response = self.teller.list_account_transactions(account)

        # overwrite all transactions that are not imported!
        for teller_tx in teller_response:
            try:
                if self.get_amount(teller_tx["amount"]) < 0:
                    if teller_tx["type"] == "payment" or "MOBILE PAYMENT" in teller_tx["description"] or "AUTOPAY PAYMENT" in teller_tx["description"]:
                        self._process_credit_or_payment(Payment, account, teller_tx)
                    else:
                        self._process_credit_or_payment(Credit, account, teller_tx)
                else:
                    self._process_transaction(account, teller_tx)
            except:
                print("Error processing teller_tx: " + json.dumps(teller_tx))
                traceback.print_exc()

        # delete all pending transactions that are not in teller_transactions!
        pending_ids = [tx["id"] for tx in teller_response if tx["status"] == "pending"]
        Transaction.delete() \
            .where(
                (Transaction.account == account.id) &
                (Transaction.status == Transaction.Status.PENDING.value) &
                (Transaction.teller_id.not_in(pending_ids))
            ) \
            .execute()

    def _process_credit_or_payment(self, model, account, teller_tx):
        if teller_tx["status"] != "posted":
            return

        id = teller_tx["id"]
        result, created = model.get_or_create(
            teller_id=id,
            defaults=self._make_transaction_args(teller_tx, account.id)
        )

        if not created:
            model.update(self._make_transaction_args(teller_tx, account.id, include_amount_and_status=False, include_unknown=False)) \
                .where(model.teller_id == id) \
                .execute()

    def _process_transaction(self, account, teller_tx):
        id = teller_tx["id"]
        result, created = Transaction.get_or_create(
            teller_id=id,
            defaults=self._make_transaction_args(teller_tx, account.id)
        )

        if not created:
            Transaction.update(self._make_transaction_args(teller_tx, account.id, include_unknown=False)) \
                .where((Transaction.status != Transaction.Status.PAID.value) & (Transaction.teller_id == id)) \
                .execute()

    def _make_transaction_args(self, tx, account_id, include_amount_and_status=True, include_unknown=True):
        args = { # always available args
            "account_id": account_id,
            "teller_id": tx["id"],
            "date": tx["date"],
            "description": tx["description"],
        }

        if include_amount_and_status:
            args["amount_usd"] = abs(self.get_amount(tx["amount"]))
            args["status"] = Transaction.Status.POSTED.value if tx["status"] == "posted" else Transaction.Status.PENDING.value

        if include_unknown:
            args["counterparty"] = "unknown"
            args["category"] = "unknown"

        if tx["details"]["counterparty"] is not None:
            args["counterparty"] = tx["details"]["counterparty"]["name"]

        if tx["details"]["category"] is not None:
            args["category"] = tx["details"]["category"]

        return args

    def get_amount(self, amount_str):
        pattern = r"^(-)?(\d*)(?:[.,](\d{0,2}))?$"
        match = re.match(pattern, amount_str)
        sign = -1 if match.group(1) else 1
        euros = int(match.group(2)) if match.group(2) else 0
        cents = int(match.group(3)) * 10 ** (2 - len(match.group(3))) if match.group(3) else 0
        return sign * (euros * 100 + cents)
