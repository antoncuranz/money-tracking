from backend.clients.teller import TellerClient
from backend.models import Transaction
from flask_injector import inject


class TransactionService:
    @inject
    def __init__(self, teller: TellerClient):
        self.teller = teller

    def import_transactions(self, account):
        teller_transactions = self.teller.list_account_transactions(account).json()[:5]  # TODO: remove [:5]

        # TODO: check if mfa is required => return 418 status!

        # overwrite all transactions that are not imported!
        for teller_tx in teller_transactions:
            id = teller_tx["id"]
            args = self.make_transaction_args(teller_tx, account.id)
            model, created = Transaction.get_or_create(
                teller_id=id,
                defaults=args
            )

            if not created:
                Transaction.update(args) \
                    .where((Transaction.status != Transaction.Status.IMPORTED.value) & (Transaction.teller_id == id)) \
                    .execute()

        # delete all pending transactions that are not in teller_transactions!
        pending_ids = [tx["id"] for tx in teller_transactions if tx["status"] == "pending"]
        Transaction.delete() \
            .where(
            (Transaction.status == Transaction.Status.PENDING.value) & (Transaction.teller_id.not_in(pending_ids))) \
            .execute()

    def make_transaction_args(self, tx, account_id):
        return {
            "account_id": account_id,
            "teller_id": tx["id"],
            "date": tx["date"],
            "description": self.get_description(tx),
            "category": tx["details"]["category"],
            "amount_usd": int(tx["amount"].replace(".", "")),
            "status": Transaction.Status.POSTED.value if tx["status"] == "posted" else Transaction.Status.PENDING.value
        }

    def get_description(self, tx):
        payee = tx["details"]["counterparty"]["name"]
        description = tx["description"]

        if payee != description:
            return "{}: {}".format(payee, description)
        else:
            return description
