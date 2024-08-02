from backend.clients.teller import TellerClient
from backend.models import *
from flask import abort, Blueprint
from peewee import *

from backend.service.actual_service import ActualService
from backend.service.conversion_service import ConversionService
from backend.service.transaction_service import TransactionService

api = Blueprint("api", __name__)


@api.get("/api/accounts")
def get_accounts():
    return list(Account.select().dicts())


@api.get("/api/accounts/<account_id>/balances")
def get_balances(account_id, teller: TellerClient):
    return teller.get_account_balances(account_id).json()


@api.get("/api/accounts/<account_id>/transactions")
def get_transactions(account_id):
    return list(Transaction.select().where(Transaction.account == account_id).order_by(-Transaction.date).dicts())


@api.post("/api/import/<account_id>")
def import_transactions(account_id, transaction_service: TransactionService, conversion_service: ConversionService):
    try:
        account = Account.get(Account.id == account_id)
    except DoesNotExist:
        abort(404)

    transaction_service.import_transactions(account)

    conversion_service.add_missing_eur_amounts()

    return "", 204


@api.post("/api/actual/<account_id>")
def import_transactions_to_actual(account_id, actual_service: ActualService):
    try:
        account = Account.get(Account.id == account_id)
    except DoesNotExist:
        abort(404)

    actual_service.import_transactions(account)

    return "", 204
