from flask import abort, Blueprint, request

from backend.clients.teller import TellerInteractionRequiredException
from backend.models import *
from backend.service.actual_service import ActualService
from backend.service.exchange_service import ExchangeService
from backend.service.transaction_service import TransactionService

imports = Blueprint("imports", __name__, url_prefix="/api/import")


@imports.post("/<account_id>")
def import_transactions(account_id, transaction_service: TransactionService, exchange_service: ExchangeService, actual_service: ActualService):
    try:
        account = Account.get(Account.id == account_id)
    except DoesNotExist:
        abort(404)

    access_token = request.args.get("access_token")
    if access_token is not None:
        account.teller_access_token = access_token
        account.save()

    enrollment = request.args.get("enrollment_id")
    if enrollment is not None:
        account.teller_enrollment_id = enrollment
        account.save()

    try:
        transaction_service.import_transactions(account)
    except TellerInteractionRequiredException:
        return "", 418

    exchange_service.add_missing_eur_amounts(account)
    actual_service.import_transactions(account)
    actual_service.import_payments(account)

    return "", 204
