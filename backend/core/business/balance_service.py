from decimal import Decimal
from typing import Annotated

from fastapi import Depends
from peewee import fn

from backend.models import ExchangePayment, Exchange, Credit, CreditTransaction, Transaction, Payment, Account


class BalanceService:
    def calc_balance_exchanged(self) -> int:
        balance = 0

        for exchange in Exchange.select():
            balance += self.calc_exchange_remaining(exchange, include_not_processed=True)

        return balance

    def calc_exchange_remaining(self, exchange: Exchange, include_not_processed=False) -> int:
        balance = exchange.amount_usd

        query = ExchangePayment.select().where(ExchangePayment.exchange == exchange)

        for exchange_payment in query:
            # TODO: check if "not" is correct
            if not include_not_processed or exchange_payment.payment.status_enum == Payment.Status.PROCESSED:
                balance -= exchange_payment.amount

        if balance < 0:
            raise Exception(f"Error: Exchange balance for exchange {exchange.id} is negative!")

        return balance

    def calc_balance_credits(self) -> int:
        balance = 0

        for credit in Credit.select():
            balance += self.calc_credit_remaining(credit)

        return balance

    def calc_credit_remaining(self, credit: Credit) -> int:
        balance = credit.amount_usd

        query = CreditTransaction.select().where(CreditTransaction.credit == credit.id)

        for credit_transaction in query:
            balance -= credit_transaction.amount

        if balance < 0:
            raise Exception(f"Error: Credit balance for credit {credit.id} is negative!")

        return balance

    def calc_transaction_remaining(self, tx: Transaction) -> int:
        balance = tx.amount_usd

        query = CreditTransaction.select().where(CreditTransaction.transaction == tx.id)

        for credit_transaction in query:
            balance -= credit_transaction.amount

        if balance < 0:
            raise Exception(f"Error: Transaction balance for transaction {tx.id} is negative!")

        return balance

    def calc_payment_remaining(self, payment: Payment) -> int:
        balance = payment.amount_usd

        query = ExchangePayment.select().where(ExchangePayment.payment == payment.id)

        for exchange_payment in query:
            balance -= exchange_payment.amount

        if balance < 0:
            raise Exception(f"Error: Payment balance for payment {payment.id} is negative!")

        return balance

    def get_account_balances(self, user):
        result = {}
        for account in Account.select().where(Account.user == user.id):
            posted_tx = Transaction.select(fn.SUM(Transaction.amount_usd)).where(
                (Transaction.account == account.id) & (Transaction.status != Transaction.Status.PENDING.value)
            ).scalar() or 0
            posted_credits = Credit.select(fn.SUM(Credit.amount_usd)).where(
                (Credit.account == account.id)).scalar() or 0
            posted_payments = Payment.select(fn.SUM(Payment.amount_usd)).where(
                (Payment.account == account.id) & (Payment.status != Payment.Status.PENDING.value)).scalar() or 0

            pending = Transaction.select(fn.SUM(Transaction.amount_usd)).where(
                (Transaction.account == account.id) & (Transaction.status == Transaction.Status.PENDING.value) &
                (Transaction.ignore.is_null() | ~Transaction.ignore)
            ).scalar() or 0

            result[account.id] = {
                "posted": posted_tx - posted_credits - posted_payments,
                "pending": pending,
                "total_spent": posted_tx,
                "total_credits": posted_credits
            }

        return result

    def get_balance_posted(self) -> int:
        transactions = Transaction.select().where(Transaction.status == Transaction.Status.POSTED.value)

        balance = 0
        for tx in transactions:
            amount = tx.amount_usd
            for ct in CreditTransaction.select().where(CreditTransaction.transaction == tx.id):
                amount -= ct.amount

            balance += amount

        return balance

    def get_balance_pending(self) -> int:
        return Transaction.select(fn.SUM(Transaction.amount_usd)) \
            .where((Transaction.status == Transaction.Status.PENDING.value) & (Transaction.ignore.is_null() | ~Transaction.ignore)).scalar() or 0

    def get_balance_credits(self) -> int:
        credits = Credit.select()

        balance = 0
        for credit in credits:
            balance += self.calc_credit_remaining(credit)

        return balance

    def get_virtual_account_balance(self) -> str:
        payments = Payment.select().where(Payment.status == Payment.Status.POSTED.value)
        remaining_payments = 0
        for payment in payments:
            remaining_payments += self.calc_payment_remaining(payment)

        virtual_balance = 0

        exchanges = Exchange.select().order_by(Exchange.date)
        for exchange in exchanges:
            remaining = self.calc_exchange_remaining(exchange)

            minimum = min(remaining_payments, remaining)
            remaining_payments -= minimum
            remaining -= minimum

            virtual_balance += round(Decimal(remaining)/exchange.amount_usd * exchange.amount_eur)

        if virtual_balance > 0:
            return str(virtual_balance)
        else:
            return "negative"

    def get_fees_and_risk_eur(self) -> int:
        return Transaction.select(fn.SUM(Transaction.fees_and_risk_eur)) \
            .where(Transaction.status == Transaction.Status.PAID.value).scalar()

BalanceServiceDep = Annotated[BalanceService, Depends()]