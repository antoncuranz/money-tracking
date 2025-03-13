import os
import uuid
from typing import Annotated, List

from fastapi import Depends, HTTPException
from sqlmodel import Session

from config import config
from data_export.adapter import openapi
from data_export.adapter.actual_client import IActualClient, ActualClient
from data_export.dataaccess.dataexport_repository import DataExportRepository
from exchangerate.facade import ExchangeRateFacade
from models import Transaction, Payment, User, Account


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
        category = os.getenv("ACTUAL_CAT_" + (tx.category or "unknown").upper(), None)
        amount_eur = tx.amount_eur or self.exchangerate.guess_amount_eur(session, tx) or 0

        if user.super_user:
            actual_tx = self._create_actual_transaction_super_user(tx, id, category, amount_eur)
        else:
            actual_tx = self._create_actual_transaction_regular(tx, id, category, amount_eur)
        self.actual.create_transaction(account, actual_tx)

        tx.actual_id = id
        session.add(tx)
        session.commit()

    def update_transactions(self, session: Session, user: User, account_id: int,
                            transactions: List[Transaction] | None = None):
        if transactions is None:
            transactions = self.repository.get_updatable_transactions(session, account_id)

        existing_payees = {payee.name: payee.id for payee in self.actual.get_payees(user)}

        for tx in transactions:
            self.update_transaction(session, user, account_id, tx, existing_payees)

    def update_transaction(self, session: Session, user: User, account_id: int, tx: Transaction, existing_payees=None):
        account = self.repository.get_account(session, user, account_id)
        if not account:
            raise HTTPException(status_code=404)

        if existing_payees is None:
            existing_payees = {payee.name: payee.id for payee in self.actual.get_payees(user)}

        if tx.actual_id is None:
            self.export_transaction(session, user, account_id, tx)

        actual_tx = self.actual.get_transaction(account, tx)
        if not actual_tx:
            raise Exception("Actual Transaction not found")

        payee = self._get_or_create_payee(user, tx, actual_tx, existing_payees)
        amount_eur = self.exchangerate.guess_amount_eur(session, tx) or 0 if tx.amount_eur is None else tx.amount_eur
        
        if user.super_user:
            fees_and_risk_eur = tx.fees_and_risk_eur if tx.fees_and_risk_eur is not None else 0
            self._update_transaction_super_user(account, tx, actual_tx, payee, amount_eur, fees_and_risk_eur)
        else:
            self._update_transaction_regular(account, tx, actual_tx, payee, amount_eur)

    def export_payment(self, session: Session, super_user: User, account_id: int, payment: Payment):
        account = self.repository.get_account(session, super_user, account_id)
        if not account:
            raise HTTPException(status_code=404)

        if payment.status_enum != Payment.Status.PROCESSED or payment.actual_id is not None:
            print("Payment status: " + str(payment.status_enum))
            print("Payment actual_id: " + str(payment.actual_id))
            raise Exception("Error: Payment not processed or already exported!")

        id = str(uuid.uuid4())

        if account.user.super_user:
            self.actual.create_transaction(account, self._create_actual_payment(payment, id))
        else:
            transactions = self.repository.get_paid_transactions_by_payment(session, payment.id)
            self.actual.create_transaction_super_misc(super_user, self._create_actual_payment_misc(payment, transactions, id))

        payment.actual_id = id
        session.add(payment)
        session.commit()

    def delete_payment(self, super_user: User, actual_id: str):
        self.actual.delete_transaction(super_user, actual_id)

    def _get_or_create_payee(self, user: User, tx: Transaction, actual_tx: openapi.Transaction, existing_payees):
        if actual_tx.payee == config.actual_unknown_payee:
            if tx.counterparty in existing_payees:
                print("Assigning existing payee for transaction with unknown payee ({})".format(tx.description))
                return existing_payees[tx.counterparty]
            else:
                print("Creating new payee for transaction with unknown payee ({})".format(tx.description))
                payee = self.actual.create_payee(user, tx.counterparty)
                existing_payees[tx.counterparty] = payee
                return payee
        else:
            return actual_tx.payee

    def _create_actual_transaction_super_user(self, tx: Transaction, id: str, category: str,
                                              amount_eur: int) -> openapi.Transaction:
        return openapi.Transaction(
            id=id,
            date=str(tx.date),
            amount=-amount_eur,
            payee_name=tx.counterparty,
            imported_payee=tx.counterparty,
            category=category,
            notes=tx.description,
            imported_id=tx.import_id,
            cleared=False,
            subtransactions=[
                openapi.Transaction(
                    amount=-amount_eur,
                    category=category,
                    notes="Original value in EUR"
                ),
                openapi.Transaction(
                    amount=0,
                    category=config.actual_fee_category,
                    notes="FX Fees and CCY Risk"
                )
            ]
        )

    def _create_actual_transaction_regular(self, tx: Transaction, id: str, category: str,
                                           amount_eur: int) -> openapi.Transaction:
        return openapi.Transaction(
            id=id,
            date=str(tx.date),
            amount=-amount_eur,
            payee_name=tx.counterparty,
            imported_payee=tx.counterparty,
            category=category,
            notes=tx.description,
            imported_id=tx.import_id,
            cleared=False,
        )

    def _create_actual_payment(self, payment: Payment, id: str) -> openapi.Transaction:
        return openapi.Transaction(
            id=id,
            date=str(payment.date),
            amount=payment.amount_eur,
            payee_name=payment.counterparty,
            imported_payee=payment.counterparty,
            notes=payment.description,
            imported_id=payment.import_id,
            cleared=True
        )
    
    def _create_actual_payment_misc(self, payment: Payment, transactions: List[Transaction], id: str) -> openapi.Transaction:
        tx_eur_sum = sum([tx.amount_eur for tx in transactions])
        fees = payment.amount_eur - tx_eur_sum
        notes = "({}) {}".format(payment.account.user.name.title(), payment.description)

        return openapi.Transaction(
            id=id,
            date=str(payment.date),
            amount=payment.amount_eur,
            payee_name=payment.counterparty,
            imported_payee=payment.counterparty,
            notes=notes,
            imported_id=payment.import_id,
            cleared=True,
            subtransactions=[
                openapi.Transaction(
                    amount=tx_eur_sum,
                    notes="Original value in EUR"
                ),
                openapi.Transaction(
                    amount=fees,
                    category=config.actual_fee_category,
                    notes="FX Fees and CCY Risk"
                )
            ]
        )

    def _update_transaction_super_user(self, account: Account, tx: Transaction, actual_tx: openapi.Transaction,
                                       payee: str, amount_eur: int, fees_and_risk_eur: int):
        fee_split = next(sub for sub in actual_tx.subtransactions if sub.category == config.actual_fee_category)
        main_split = next(sub for sub in actual_tx.subtransactions if sub.category != config.actual_fee_category)

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

    def _update_transaction_regular(self, account: Account, tx: Transaction, actual_tx: openapi.Transaction, payee: str,
                                    amount_eur: int):
        self.actual.patch_transaction(account, actual_tx, {
            "cleared": True,  # TODO: make dynamic also for regular users (requires updating payments after (un)processing)
            "amount": -amount_eur,
            "date": str(tx.date),
            "payee": payee,
            "imported_payee": tx.counterparty,
            "notes": tx.description,
        })
