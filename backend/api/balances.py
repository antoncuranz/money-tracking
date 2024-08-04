from flask import Blueprint

from backend.models import *
from backend.service.balance_service import BalanceService

balances = Blueprint("balances", __name__, url_prefix="/api/balance")


@balances.get("/total")
def get_balance_total(balance_service: BalanceService):
    balance = Transaction.select(fn.SUM(Transaction.amount_usd)) \
        .where(Transaction.status != Transaction.Status.PAID.value).scalar()

    balance -= balance_service.calc_balance_exchanged()
    return str(balance), 200


@balances.get("/posted")
def get_balance_posted():
    transactions = Transaction.select().where(Transaction.status == Transaction.Status.POSTED.value)

    balance = 0
    for tx in transactions:
        amount = tx.amount_usd
        for ct in CreditTransaction.select().where(CreditTransaction.transaction == tx.id):
            amount += ct.amount

        balance += amount

    return str(balance), 200


@balances.get("/pending")
def get_balance_pending():
    balance = Transaction.select(fn.SUM(Transaction.amount_usd)) \
        .where(Transaction.status == Transaction.Status.PENDING.value).scalar()
    return str(balance), 200


@balances.get("/exchanged")
def get_balance_exchanged(balance_service: BalanceService):
    balance = balance_service.calc_balance_exchanged()
    return str(balance), 200
