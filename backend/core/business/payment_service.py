from decimal import Decimal
from typing import List, Annotated

from fastapi import Depends, HTTPException
from sqlmodel import Session

from core.business.balance_service import BalanceService
from core.business.exchange_service import ExchangeService
from core.dataaccess.store import Store
from data_export.facade import DataExportFacade
from models import Transaction, ExchangePayment, Payment, User


class PaymentService:
    def __init__(self, store: Annotated[Store, Depends()],
                 balance_service: Annotated[BalanceService, Depends()],
                 exchange_service: Annotated[ExchangeService, Depends()],
                 data_export: Annotated[DataExportFacade, Depends()]):
        self.store = store
        self.balance_service = balance_service
        self.exchange_service = exchange_service
        self.data_export = data_export
    
    def get_payments(self, session: Session, user: User, account_id: int, processed: bool | None = None):
        return self.store.get_payments(session, user, account_id, processed)

    def process_payment(self, session: Session, user: User, payment_id: int, transactions=None):
        payment = self.store.get_payment(session, user, payment_id)
        if not payment:
            raise HTTPException(status_code=404)

        if not transactions:
            transactions = self._guess_transactions_to_process(session, payment)
        
        self._process_payment(session, payment, transactions)
    
        self.data_export.update_transactions(session, user, payment.account.id, transactions)
        self.data_export.export_payment(session, user, payment.account.id, payment)
    
    def unprocess_payment(self, session: Session, user: User, payment_id: int):
        payment = self.store.get_payment(session, user, payment_id)
        if not payment:
            raise HTTPException(status_code=404)
        
        payment.status_enum = Payment.Status.POSTED
        payment.amount_eur = None
        payment.actual_id = None
        session.add(payment)

        transactions = self.store.get_paid_transactions_by_payment(session, user, payment_id)
        for tx in transactions:
            tx.status_enum = Transaction.Status.POSTED
            tx.payment = None
            tx.fees_and_risk_eur = None
            session.add(tx)
        session.commit()

        self.data_export.update_transactions(session, user, payment.account.id, transactions)
            
        if payment.actual_id is not None:
            self.data_export.delete_transaction(user, payment.actual_id)

    def _guess_transactions_to_process(self, session: Session, payment: Payment):
        transactions = self.store.get_posted_transactions_by_account(session, payment.account.id)

        process_tx = []
        amount = payment.amount_usd

        for tx in transactions:
            tx_remaining = self.balance_service.calc_transaction_remaining(session, tx)
            if 0 < amount < tx_remaining:
                raise Exception("Error finding transactions automatically.")

            if amount > 0:
                process_tx.append(tx)
                amount -= tx_remaining
            else:
                break

        return process_tx

    def _process_payment(self, session: Session, payment: Payment, transactions: List[Transaction]):
        if any(tx.amount_eur is None for tx in transactions):
            raise Exception("Error: All transactions must have amount_eur set!")
        
        if payment.status_enum == Payment.Status.PENDING:
            raise Exception("Error: Payment is still pending!")

        if payment.status_enum == Payment.Status.PROCESSED or len(payment.transactions) > 0:
            raise Exception("Error: Payment was already processed!")

        tx_remaining_sum = sum([self.balance_service.calc_transaction_remaining(session, tx) for tx in transactions])
        if payment.amount_usd != tx_remaining_sum:
            raise Exception("Error: Payment amount does not match sum of transactions!")

        exchange_payments = self.store.get_exchange_payments_by_payment(session, payment.id)
        amount_eur = self._calc_payment_amount_eur(exchange_payments)

        for tx in transactions:
            tx.fees_and_risk_eur = self._calc_fees_and_risk(session, tx, payment, exchange_payments, amount_eur)
            tx.payment_id = payment.id
            tx.status_enum = Transaction.Status.PAID
            session.add(tx)

        payment.amount_eur = round(amount_eur)
        payment.status_enum = Payment.Status.PROCESSED
        session.add(payment)

        eur_sum = sum([tx.amount_eur + tx.fees_and_risk_eur for tx in transactions])
        eur_err = payment.amount_eur - eur_sum
        print("Calculated eur_err of " + str(eur_err)) # TODO: send notification or display in frontend

        # apply error to largest transaction
        largest_tx = max(transactions, key=lambda tx: tx.amount_eur or 0)
        largest_tx.fees_and_risk_eur += eur_err
        session.add(largest_tx)
        session.commit()

    def _calc_fees_and_risk(self, session: Session, tx: Transaction, payment: Payment, exchange_payments: List[ExchangePayment], payment_amount_eur: Decimal) -> int:
        neutral_sum = self._calc_neutral_sum(exchange_payments)
        eur_usd_exchanged = Decimal(payment.amount_usd - neutral_sum) / payment_amount_eur
        
        if tx.amount_eur == 0:
            return 0

        amount_usd = self.balance_service.calc_transaction_remaining(session, tx)
        value_eur_exchanged = amount_usd / eur_usd_exchanged
        effective_fees_total = value_eur_exchanged - tx.amount_eur

        return round(effective_fees_total)


    def _calc_payment_amount_eur(self, exchange_payments: List[ExchangePayment]) -> Decimal:
        amount_eur = Decimal(0)
        for ep in exchange_payments:
            if ep.exchange.paid_eur != 0:  # ignore neutral exchanges
                amount_eur += (Decimal(ep.amount) / Decimal(ep.exchange.amount_usd)) * ep.exchange.amount_eur

        return amount_eur
    
    
    def _calc_neutral_sum(self, exchange_payments: List[ExchangePayment]) -> int:
        # Ignore "neutral" exchanges (i.e. exchange.paid_eur == 0). Ignored exchanges won't affect the avg rate.

        neutral_sum = 0
        for ep in exchange_payments:
            if ep.exchange.paid_eur == 0:
                neutral_sum += ep.amount

        return neutral_sum
