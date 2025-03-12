import os
import uuid
from typing import Annotated, List

from fastapi import Depends, HTTPException
from sqlmodel import Session

from config import config
from data_export.adapter.actual_client import IActualClient, ActualClient
from data_export.dataaccess.dataexport_repository import DataExportRepository
from exchangerate.facade import ExchangeRateFacade
from models import Transaction, Payment, User


class ActualService:
    def __init__(self, actual: Annotated[IActualClient, Depends(ActualClient)],
                 exchangerate: Annotated[ExchangeRateFacade, Depends()],
                 repository: Annotated[DataExportRepository, Depends()]):
        self.actual = actual
        self.exchangerate = exchangerate
        self.repository = repository

    def export_transactions(self, session: Session, user: User, account_id: int):
        transactions = self.repository.get_unexported_transactions(session, account_id)

        for tx in transactions:
            self.export_transaction(session, user, account_id, tx)

    def export_transaction(self, session: Session, user: User, account_id: int, tx: Transaction):
        account = self.repository.get_account(session, user, account_id)
        if not account:
            raise HTTPException(status_code=404)
        
        print("Exporting transaction to Actual: " + str(tx))
        id = str(uuid.uuid4())
        self.actual.create_transaction(account, self._create_actual_transaction(session, tx, id))
        tx.actual_id = id
        session.add(tx)
        session.commit()

    def update_transactions(self, session: Session, user: User, account_id: int, transactions: List[Transaction] | None = None):
        if transactions is None:
            transactions = self.repository.get_updatable_transactions(session, account_id)
            
        existing_payees = {payee["name"]: payee["id"] for payee in self.actual.get_payees(user)['data']}

        for tx in transactions:
            self.update_transaction(session, user, account_id, tx, existing_payees)

    def update_transaction(self, session: Session, user: User, account_id: int, tx: Transaction, existing_payees=None):
        account = self.repository.get_account(session, user, account_id)
        if not account:
            raise HTTPException(status_code=404)
        
        if existing_payees is None:
            existing_payees = {payee["name"]: payee["id"] for payee in self.actual.get_payees(user)['data']}

        if tx.actual_id is None:
            self.export_transaction(session, user, account_id, tx)

        actual_tx = self.actual.get_transaction(account, tx)
        payee = self._get_or_create_payee(account.user, tx, actual_tx, existing_payees)

        fee_split = next(sub for sub in actual_tx["subtransactions"] if sub["category"] == config.actual_fee_category)
        main_split = next(sub for sub in actual_tx["subtransactions"] if sub["category"] != config.actual_fee_category)

        amount_eur = self.exchangerate.guess_amount_eur(session, tx) or 0 if tx.amount_eur is None else tx.amount_eur
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

    def export_payments(self, session: Session, user: User, account_id: int):
        payments = self.repository.get_unexported_payments(session, account_id)

        for payment in payments:
            self.export_payment(session, user, account_id, payment)

    def export_payment(self, session: Session, user: User, account_id: int, payment: Payment):
        account = self.repository.get_account(session, user, account_id)
        if not account:
            raise HTTPException(status_code=404)
        
        if payment.status_enum != Payment.Status.PROCESSED or payment.actual_id is not None:
            print("Payment status: " + str(payment.status_enum))
            print("Payment actual_id: " + str(payment.actual_id))
            raise Exception("Error: Payment not processed or already exported!")

        id = str(uuid.uuid4())
        self.actual.create_transaction(account, self._create_actual_payment(payment, id))
        payment.actual_id = id
        session.add(payment)
        session.commit()

    def delete_transaction(self, user: User, actual_id: str):
        self.actual.delete_transaction(user, actual_id)

    def _create_actual_transaction(self, session: Session, tx: Transaction, id: str):
        category = os.getenv("ACTUAL_CAT_" + (tx.category or "unknown").upper(), None)
        amount_eur = tx.amount_eur or self.exchangerate.guess_amount_eur(session, tx) or 0
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

    def _create_actual_payment(self, payment: Payment, id: str):
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
