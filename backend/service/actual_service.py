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
            self.actual.import_transactions(account.actual_id, [self.create_actual_transaction(tx)])
            tx.status_enum = Transaction.Status.IMPORTED
            tx.save()

    def create_actual_transaction(self, tx):
        return {
            # "account": actual_account_id,
            "date": str(tx.date),
            "amount": tx.amount_eur,  # TODO
            "payee_name": tx.description,
            "imported_payee": tx.description,
            "category": Config.actual_other_category,
            "notes": "Imported using API",
            "imported_id": tx.teller_id,
            "cleared": True,
            "subtransactions": [
                {
                    "amount": tx.amount_eur,
                    "category": Config.actual_other_category,
                    "notes": "Original value in EUR"
                },
                {
                    "amount": 0,  # TODO
                    "category": Config.actual_fee_category,
                    "notes": "Effective FX fees"
                },
                {
                    "amount": 0,  # TODO
                    "category": Config.actual_fee_category,
                    "notes": "Currency Risk"
                }
            ]
        }
