from flask import abort, Blueprint, request, g

from backend.core.service.transaction_service import TransactionService
from backend.core.util import stringify, parse_boolean
from backend.models import Transaction
from peewee import DoesNotExist

from backend.core.service.exchange_service import ExchangeService

transactions = Blueprint("transactions", __name__, url_prefix="/api/transactions")

def map_transaction(transaction: Transaction, exchange_service: ExchangeService):
    dict = stringify(transaction)
    dict["guessed_amount_eur"] = exchange_service.guess_amount_eur(transaction)
    return dict


@transactions.get("")
def get_transactions(transaction_service: TransactionService, exchange_service: ExchangeService):
    try:
        account_str = request.args.get("account")
        account_id = None if not account_str else int(account_str)
        paid = parse_boolean(request.args.get("paid"))
    except (ValueError, TypeError):
        abort(400)

    transactions = transaction_service.get_transactions(g.user, account_id, paid)
    return [map_transaction(tx, exchange_service) for tx in transactions]


@transactions.put("/<tx_id>")
def update_transaction(tx_id, transaction_service: TransactionService):
    try:
        amount_eur_str = request.args.get("amount_eur")
        amount_eur = None if not amount_eur_str else int(amount_eur_str)
    except (ValueError, TypeError):
        abort(400)
        
    try:
        transaction_service.update_transaction(g.user, tx_id, amount_eur)
    except DoesNotExist:
        abort(404)

    return "", 200
