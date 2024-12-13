from flask import abort, Blueprint, request, g

from backend.core.service.credit_service import CreditService
from backend.core.util import stringify, parse_boolean
from peewee import DoesNotExist

credits = Blueprint("credits", __name__, url_prefix="/api/credits")


@credits.get("")
def get_credits(credit_service: CreditService):
    try:
        account_str = request.args.get("account")
        account_id = None if not account_str else int(account_str)
        usable = parse_boolean(request.args.get("usable"))
    except (ValueError, TypeError):
        abort(400)

    credits = credit_service.get_credits(g.user, account_id, usable)
    return [stringify(credit) for credit in credits]


@credits.put("/<credit_id>")
def update_credit(credit_id, credit_service: CreditService):
    try:
        amount = int(request.args.get("amount"))
        transaction_id = int(request.args.get("transaction"))
    except (ValueError, TypeError):
        abort(400)

    try:
        credit_service.update_credit(g.user, credit_id, transaction_id, amount)
    except DoesNotExist:
        abort(404)

    return "", 204
