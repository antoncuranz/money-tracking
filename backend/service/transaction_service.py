import json
import re
import traceback

from backend.clients.teller import ITellerClient, TellerInteractionRequiredException
from backend.models import Transaction, Credit, Payment
from flask_injector import inject


class TransactionService:

    @inject
    def __init__(self, teller: ITellerClient):
        self.teller = teller

    def import_transactions(self, account):
        if account.teller_enrollment_id is None or account.teller_access_token is None:
            raise TellerInteractionRequiredException()

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
                    if teller_tx["type"] == "payment" or "MOBILE PAYMENT" in teller_tx["description"]:
                        self.process_payment(account, teller_tx)
                    else:
                        self.process_credit(account, teller_tx)
                else:
                    self.process_transaction(account, teller_tx)
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

    def process_payment(self, account, teller_tx):
        if teller_tx["status"] != "posted":
            return

        Payment.get_or_create(
            teller_id=teller_tx["id"],
            defaults=self.make_transaction_args(teller_tx, account.id)
        )

    def process_credit(self, account, teller_tx):
        if teller_tx["status"] != "posted":
            return

        Credit.get_or_create(
            teller_id=teller_tx["id"],
            defaults=self.make_transaction_args(teller_tx, account.id)
        )

    def process_transaction(self, account, teller_tx):
        id = teller_tx["id"]
        args = self.make_transaction_args(teller_tx, account.id)
        model, created = Transaction.get_or_create(
            teller_id=id,
            defaults=args
        )

        if not created:
            Transaction.update(args) \
                .where((Transaction.status != Transaction.Status.PAID.value) & (Transaction.teller_id == id)) \
                .execute()
            # TODO: update Actual transactions?
            # Actual tx will be updated when payment is processed?

    def make_transaction_args(self, tx, account_id):
        counterparty = tx["details"]["counterparty"]["name"] if tx["details"]["counterparty"] is not None else "unknown"
        category = tx["details"]["category"] if tx["details"]["category"] is not None else "unknown"
        return {
            "account_id": account_id,
            "teller_id": tx["id"],
            "date": tx["date"],
            "counterparty": counterparty,
            "description": tx["description"],
            "category": category,
            "amount_usd": abs(self.get_amount(tx["amount"])),
            "status": Transaction.Status.POSTED.value if tx["status"] == "posted" else Transaction.Status.PENDING.value
        }

    def get_amount(self, amount_str):
        pattern = r"^(-)?(\d*)(?:[.,](\d{0,2}))?$"
        match = re.match(pattern, amount_str)
        sign = -1 if match.group(1) else 1
        euros = int(match.group(2)) if match.group(2) else 0
        cents = int(match.group(3)) * 10 ** (2 - len(match.group(3))) if match.group(3) else 0
        return sign * (euros * 100 + cents)
