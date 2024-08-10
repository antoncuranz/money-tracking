from backend.clients.actual import IActualClient
from backend.config import Config
from backend.models import Transaction, Account, Payment
from flask_injector import inject
import uuid


class ActualService:
    @inject
    def __init__(self, actual: IActualClient):
        self.actual = actual

    def import_transactions(self, account):
        transactions = Transaction.select().where(
            (Transaction.status != Transaction.Status.PENDING.value) &
            (Transaction.actual_id.is_null()) &
            (Transaction.amount_eur.is_null(False)) &
            (Transaction.account == account.id))

        for tx in transactions:
            self.import_transaction(account, tx)

    def import_transaction(self, account, tx):
        id = str(uuid.uuid4())
        self.actual.create_transaction(account.actual_id, self._create_actual_transaction(tx, id))
        tx.actual_id = id
        tx.save()

    def update_transactions(self, account, transactions):
        for tx in transactions:
            self.update_transaction(account, tx)

    def update_transaction(self, account, tx):
        actual_account = account.actual_id

        if tx.actual_id is None:
            self.import_transaction(account, tx)

        actual_tx = self.actual.get_transaction(actual_account, tx)

        fx_split = next(sub for sub in actual_tx["subtransactions"] if sub["category"] == Config.actual_fee_category)
        ccy_split = next(sub for sub in actual_tx["subtransactions"] if sub["category"] == Config.actual_ccy_category)
        main_split = next(sub for sub in actual_tx["subtransactions"] if sub["category"] != Config.actual_fee_category and sub["category"] != Config.actual_ccy_category)

        fx_fees = tx.fx_fees if tx.fx_fees is not None else 0
        ccy_risk = tx.ccy_risk if tx.ccy_risk is not None else 0
        self.actual.patch_transaction(actual_account, actual_tx, {
            "cleared": tx.status_enum == Transaction.Status.PAID,
            "amount": -(tx.amount_eur + fx_fees + ccy_risk),
        })
        self.actual.patch_transaction(actual_account, main_split, {"amount": -tx.amount_eur})
        self.actual.patch_transaction(actual_account, fx_split, {"amount": -fx_fees})
        self.actual.patch_transaction(actual_account, ccy_split, {"amount": -ccy_risk})

    def import_payments(self, account):
        payments = Payment.select().where(
            (Payment.actual_id.is_null()) &
            (Payment.amount_eur.is_null(False)) &
            (Payment.processed == True) &
            (Payment.account == account.id))

        for payment in payments:
            self.import_payment(account, payment)

    def import_payment(self, account, payment):
        if payment.processed is False or payment.actual_id is not None:
            raise Exception("Error: Payment not processed or already imported!")

        id = str(uuid.uuid4())
        self.actual.create_transaction(account.actual_id, self._create_actual_payment(payment, id))
        payment.actual_id = id
        payment.save()

    def _create_actual_transaction(self, tx, id):
        return {
            "id": id,
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
                    "category": Config.actual_ccy_category,
                    "notes": "Currency Risk"
                }
            ]
        }

    def _create_actual_payment(self, payment, id):
        return {
            "id": id,
            "date": str(payment.date),
            "amount": payment.amount_eur,
            "payee_name": payment.counterparty,
            "imported_payee": payment.counterparty,
            "category": Config.actual_other_category,
            "notes": payment.description,
            "imported_id": payment.teller_id,
            "cleared": True
        }
