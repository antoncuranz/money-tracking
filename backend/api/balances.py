from decimal import Decimal

from flask import Blueprint

from backend.models import *
from backend.service.balance_service import BalanceService

balances = Blueprint("balances", __name__, url_prefix="/api/balance")


@balances.get("")
def get_balances(balance_service: BalanceService):
    posted = get_balance_posted()
    pending = get_balance_pending()
    credits = get_balance_credits(balance_service)
    exchanged = balance_service.calc_balance_exchanged()
    total = posted + pending - credits - exchanged

    return {
        "total": total,
        "posted": posted,
        "pending": pending,
        "credits": credits,
        "exchanged": exchanged,
        "virtual_account": get_virtual_account_balance(balance_service)
    }


def get_balance_posted():
    transactions = Transaction.select().where(Transaction.status == Transaction.Status.POSTED.value)

    balance = 0
    for tx in transactions:
        amount = tx.amount_usd
        for ct in CreditTransaction.select().where(CreditTransaction.transaction == tx.id):
            amount -= ct.amount

        balance += amount

    return balance


def get_balance_pending():
    return Transaction.select(fn.SUM(Transaction.amount_usd)) \
        .where((Transaction.status == Transaction.Status.PENDING.value) & (Transaction.ignore.is_null() | ~Transaction.ignore)).scalar()


def get_balance_credits(balance_service: BalanceService):
    credits = Credit.select()

    balance = 0
    for credit in credits:
        balance += balance_service.calc_credit_remaining(credit)

    return balance


def get_virtual_account_balance(balance_service: BalanceService):
    payments = Payment.select().where(Payment.processed == False)
    remaining_payments = 0
    for payment in payments:
        remaining_payments += balance_service.calc_payment_remaining(payment)

    virtual_balance = 0

    exchanges = Exchange.select().order_by(Exchange.date)
    for exchange in exchanges:
        remaining = balance_service.calc_exchange_remaining(exchange)

        minimum = min(remaining_payments, remaining)
        remaining_payments -= minimum
        remaining -= minimum

        virtual_balance += round(Decimal(remaining)/exchange.amount_usd * exchange.amount_eur)

    if virtual_balance > 0:
        return str(virtual_balance)
    else:
        return "negative"
