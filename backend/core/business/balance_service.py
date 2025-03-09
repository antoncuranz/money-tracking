from decimal import Decimal
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from core.dataaccess.store import Store
from models import Exchange, Credit, Transaction, Payment, engine, User


class BalanceService:
    def __init__(self, store: Annotated[Store, Depends()]):
        self.store = store
        
    def calc_balance_exchanged(self, session: Session) -> int:
        balance = 0

        for exchange in self.store.get_exchanges(session):
            balance += self.calc_exchange_remaining(session, exchange, include_not_processed=True)

        return balance

    def calc_exchange_remaining(self, session: Session, exchange: Exchange, include_not_processed=False) -> int:
        balance = exchange.amount_usd
        query = self.store.get_exchange_payments_by_exchange(session, exchange.id)

        for exchange_payment in query:
            # TODO: check if "not" is correct
            if not include_not_processed or exchange_payment.payment.status_enum == Payment.Status.PROCESSED:
                balance -= exchange_payment.amount

        if balance < 0:
            raise Exception(f"Error: Exchange balance for exchange {exchange.id} is negative!")

        return balance

    def calc_credit_remaining(self, session: Session, credit: Credit) -> int:
        balance = credit.amount_usd

        query = self.store.get_credit_transactions_by_credit(session, credit.id)

        for credit_transaction in query:
            balance -= credit_transaction.amount

        if balance < 0:
            raise Exception(f"Error: Credit balance for credit {credit.id} is negative!")

        return balance

    def calc_transaction_remaining(self, session: Session, tx: Transaction) -> int:
        balance = tx.amount_usd

        query = self.store.get_credit_transactions_by_transaction(session, tx.id)

        for credit_transaction in query:
            balance -= credit_transaction.amount

        if balance < 0:
            raise Exception(f"Error: Transaction balance for transaction {tx.id} is negative!")

        return balance

    def calc_payment_remaining(self, session: Session, payment: Payment) -> int:
        balance = payment.amount_usd

        query = self.store.get_exchange_payments_by_payment(session, payment.id)

        for exchange_payment in query:
            balance -= exchange_payment.amount

        if balance < 0:
            raise Exception(f"Error: Payment balance for payment {payment.id} is negative!")

        return balance

    def get_account_balances(self, session: Session, user: User):
        result = {}
        accounts = self.store.get_all_accounts(session) if user.super_user else self.store.get_accounts_of_user(session, user)
        for account in accounts:
            posted_tx = self.store.get_posted_transaction_amount(session, account.id)
            posted_credits = self.store.get_posted_credit_amount(session, account.id)
            posted_payments = self.store.get_posted_payment_amount(session, account.id)
            pending = self.store.get_pending_transaction_amount(session, account.id)

            result[account.id] = {
                "posted": posted_tx - posted_credits - posted_payments,
                "pending": pending,
                "total_spent": posted_tx,
                "total_credits": posted_credits
            }

        return result

    def get_balance_posted(self, session: Session) -> int:
        transactions = self.store.get_all_posted_transactions(session)

        balance = 0
        for tx in transactions:
            amount = tx.amount_usd
            for ct in self.store.get_credit_transactions_by_transaction(session, tx.id):
                amount -= ct.amount

            balance += amount

        return balance

    def get_balance_pending(self, session: Session) -> int:
        return self.store.get_balance_pending(session)

    def get_balance_credits(self, session: Session) -> int:
        credits = self.store.get_all_credits(session)

        balance = 0
        for credit in credits:
            balance += self.calc_credit_remaining(session, credit)

        return balance

    def get_virtual_account_balance(self, session: Session) -> str:
        payments = self.store.get_all_posted_payments(session)
        remaining_payments = 0
        for payment in payments:
            remaining_payments += self.calc_payment_remaining(session, payment)

        virtual_balance = 0

        exchanges = self.store.get_exchanges(session)
        for exchange in reversed(exchanges):
            remaining = self.calc_exchange_remaining(session, exchange)

            minimum = min(remaining_payments, remaining)
            remaining_payments -= minimum
            remaining -= minimum

            virtual_balance += round(Decimal(remaining)/exchange.amount_usd * exchange.amount_eur)

        if virtual_balance > 0:
            return str(virtual_balance)
        else:
            return "negative"

    def get_fees_and_risk_eur(self, session: Session) -> int:
        return self.store.get_fees_and_risk_eur(session)
