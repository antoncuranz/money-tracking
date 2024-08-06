from flask import abort, Blueprint

from backend.api.util import stringify
from backend.clients.teller import ITellerClient
from backend.models import *

accounts = Blueprint("accounts", __name__, url_prefix="/api/accounts")


@accounts.get("")
def get_accounts():
    return list(Account.select().dicts())


@accounts.get("/<account_id>/balances")
def get_balances(account_id, teller: ITellerClient):
    try:
        account = Account.get(Account.id == account_id)
    except DoesNotExist:
        abort(404)
    return teller.get_account_balances(account)


@accounts.get("/<account_id>/transactions")
def get_transactions(account_id):
    query = Transaction.select().where(Transaction.account == account_id).order_by(-Transaction.date)
    return [stringify(tx) for tx in query]



@accounts.get("/<account_id>/payments")
def get_payments(account_id):
    query = Payment.select().where(Payment.account == account_id).order_by(-Payment.date)
    return [stringify(payment) for payment in query]