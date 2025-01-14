import os
import uuid
from typing import Annotated, List

from fastapi import Depends

from backend.config import config
from backend.core.util import stringify
from backend.data_export.adapter.actual_client import IActualClient, ActualClient
from backend.exchangerate.facade import ExchangeRateDep
from backend.models import Transaction, Payment, Account, User


class ActualService:
    def __init__(self, actual: Annotated[IActualClient, Depends(ActualClient)],
                 exchangerate: ExchangeRateDep):
        self.actual = actual
        self.exchangerate = exchangerate

    def export_transactions(self, account: Account):
        transactions = Transaction.select().where(
            (Transaction.status != Transaction.Status.PENDING.value) &
            (Transaction.actual_id.is_null()) &
            (Transaction.account == account.id))

        for tx in transactions:
            self.export_transaction(account, tx)

    def export_transaction(self, account: Account, tx: Transaction):
        print("Importing transaction in Actual: " + str(stringify(tx)))
        id = str(uuid.uuid4())
        self.actual.create_transaction(account, self._create_actual_transaction(tx, id))
        tx.actual_id = id
        tx.save()

    def update_transactions(self, account: Account, transactions: List[Transaction] | None = None):
        if transactions is None:
            transactions = Transaction.select().where(
                (Transaction.status == Transaction.Status.POSTED.value) &
                (Transaction.actual_id.is_null(False)) &
                (Transaction.amount_eur.is_null(False)) &
                (Transaction.account == account.id))
            
        existing_payees = {payee["name"]: payee["id"] for payee in self.actual.get_payees(account.user)['data']}

        for tx in transactions:
            self.update_transaction(account, tx, existing_payees)

    def update_transaction(self, account: Account, tx: Transaction, existing_payees=None):
        if existing_payees is None:
            existing_payees = {payee["name"]: payee["id"] for payee in self.actual.get_payees(account.user)['data']}

        if tx.actual_id is None:
            self.export_transaction(account, tx)

        actual_tx = self.actual.get_transaction(account, tx)
        payee = self._get_or_create_payee(account.user, tx, actual_tx, existing_payees)

        fee_split = next(sub for sub in actual_tx["subtransactions"] if sub["category"] == config.actual_fee_category)
        main_split = next(sub for sub in actual_tx["subtransactions"] if sub["category"] != config.actual_fee_category)

        amount_eur = tx.amount_eur or self.exchangerate.guess_amount_eur(tx) or 0
        fees_and_risk_eur = tx.fees_and_risk_eur if tx.fees_and_risk_eur is not None else 0
        self.actual.patch_transaction(account, actual_tx, {
            "cleared": tx.status_enum == Transaction.Status.PAID,
            "amount": -(amount_eur + fees_and_risk_eur),
            "date": str(tx.date),
            "payee": payee,
            "imported_payee": tx.counterparty,
            "notes": tx.description,
        })
        self.actual.patch_transaction(account, main_split, {
            "amount": -amount_eur,
            "date": str(tx.date),
            "payee": payee,
            "imported_payee": tx.counterparty,
        })
        self.actual.patch_transaction(account, fee_split, {
            "amount": -fees_and_risk_eur,
            "date": str(tx.date),
            "payee": payee,
            "imported_payee": tx.counterparty,
        })
        
    def export_payments(self, account: Account):
        payments = Payment.select().where(
            (Payment.actual_id.is_null()) &
            (Payment.amount_eur.is_null(False)) &
            (Payment.status == Payment.Status.PROCESSED.value) &
            (Payment.account == account.id))

        for payment in payments:
            self.export_payment(account, payment)

    def export_payment(self, account: Account, payment: Payment):
        if payment.status_enum != Payment.Status.PROCESSED or payment.actual_id is not None:
            raise Exception("Error: Payment not processed or already imported!")

        id = str(uuid.uuid4())
        self.actual.create_transaction(account, self._create_actual_payment(payment, id))
        payment.actual_id = id
        payment.save()

    def delete_transaction(self, user: User, actual_id: int):
        self.actual.delete_transaction(user, actual_id)

    def _create_actual_transaction(self, tx: Transaction, id: str):
        category = os.getenv("ACTUAL_CAT_" + (tx.category or "unknown").upper(), None)
        amount_eur = tx.amount_eur or self.exchangerate.guess_amount_eur(tx) or 0
        return {
            "id": id,
            "date": str(tx.date),
            "amount": -amount_eur,
            "payee_name": tx.counterparty,
            "imported_payee": tx.counterparty,
            "category": category,
            "notes": tx.description,
            "imported_id": tx.import_id,
            "cleared": False,
            "subtransactions": [
                {
                    "amount": -amount_eur,
                    "category": category,
                    "notes": "Original value in EUR"
                },
                {
                    "amount": 0,
                    "category": config.actual_fee_category,
                    "notes": "FX Fees and CCY Risk"
                }
            ]
        }

    def _create_actual_payment(self, payment: Payment, id: int):
        return {
            "id": id,
            "date": str(payment.date),
            "amount": payment.amount_eur,
            "payee_name": payment.counterparty,
            "imported_payee": payment.counterparty,
            "notes": payment.description,
            "imported_id": payment.import_id,
            "cleared": True
        }

    def _get_or_create_payee(self, user: User, tx: Transaction, actual_tx, existing_payees):
        if actual_tx["payee"] == config.actual_unknown_payee:
            if tx.counterparty in existing_payees:
                print("Assigning existing payee for transaction with unknown payee ({})".format(tx.description))
                return existing_payees[tx.counterparty]
            else:
                print("Creating new payee for transaction with unknown payee ({})".format(tx.description))
                payee = self.actual.create_payee(user, tx.counterparty)["data"]
                existing_payees[tx.counterparty] = payee
                return payee
        else:
            return actual_tx["payee"]

ActualServiceDep = Annotated[ActualService, Depends()]