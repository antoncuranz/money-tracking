from backend.clients.actual import ActualClient
from backend.config import Config
from backend.models import Transaction
from flask_injector import inject


class ActualService:
    @inject
    def __init__(self, actual: ActualClient):
        self.actual = actual

    def import_transactions(self, account):
        transactions = Transaction.select().where(
            (Transaction.status == Transaction.Status.POSTED.value) &
            (Transaction.amount_eur.is_null(False)) &
            (Transaction.account == account.id))

        for tx in transactions:
            response = self.actual.import_transactions(account.actual_id, [self.create_actual_transaction(tx)])
            tx.actual_id = response["data"]["added"][0]
            tx.save()

    def create_actual_transaction(self, tx):
        return {
            "date": str(tx.date),
            "amount": -tx.amount_eur,
            "payee_name": tx.counterparty,
            "imported_payee": tx.counterparty,
            "category": Config.actual_other_category,
            "notes": tx.description,
            "imported_id": tx.teller_id,
            "cleared": False,
            "subtransactions": [
                {
                    "amount": -tx.amount_eur,
                    "category": Config.actual_other_category,
                    "notes": "Original value in EUR"
                },
                {
                    "amount": 0,
                    "category": Config.actual_fee_category,
                    "notes": "Effective FX fees"
                },
                {
                    "amount": 0,
                    "category": Config.actual_fee_category,
                    "notes": "Currency Risk"
                }
            ]
        }
