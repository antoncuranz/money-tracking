from flask import abort, Blueprint, request

from backend.api.util import stringify, parse_boolean
from backend.models import Account, Transaction
from peewee import DoesNotExist

transactions = Blueprint("transactions", __name__, url_prefix="/api/transactions")


@transactions.get("")
def get_transactions():
    try:
        account_str = request.args.get("account")
        account_id = None if not account_str else int(account_str)
        paid = parse_boolean(request.args.get("paid"))
    except (ValueError, TypeError):
        abort(400)

    query = True

    if paid is True:
        query = query & (Transaction.status == Transaction.Status.PAID.value)
    elif paid is False:
        query = query & (Transaction.status != Transaction.Status.PAID.value)

    if account_id is not None:
        try:
            Account.get(Account.id == account_id)
        except DoesNotExist:
            abort(404)
        query = query & (Transaction.account == account_id)

    transactions = Transaction.select().where(query).order_by(-Transaction.date)
    return [stringify(tx) for tx in transactions]


@transactions.put("/<tx_id>")
def update_transaction(tx_id):
    try:
        amount_eur_str = request.args.get("amount_eur")
        amount_eur = None if not amount_eur_str else int(amount_eur_str)
        transaction = Transaction.get(Transaction.id == tx_id)
    except DoesNotExist:
        abort(404)
    except (ValueError, TypeError):
        abort(400)

    transaction.amount_eur = amount_eur
    transaction.save()

    return "", 200
