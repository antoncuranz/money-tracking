from flask import abort, Blueprint

from backend.clients.teller import ITellerClient
from backend.models import Account
from peewee import DoesNotExist

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
