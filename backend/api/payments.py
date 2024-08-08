from flask import abort, Blueprint, request

from backend.api.util import stringify, parse_boolean
from backend.models import Account, Payment
from peewee import DoesNotExist

payments = Blueprint("payments", __name__, url_prefix="/api/payments")


@payments.get("")
def get_payments():
    try:
        account_str = request.args.get("account")
        account_id = None if not account_str else int(account_str)
        processed = parse_boolean(request.args.get("processed"))
    except (ValueError, TypeError):
        abort(400)

    query = True

    if processed is not None:
        query = query & (Payment.processed == processed)

    if account_id is not None:
        try:
            Account.get(Account.id == account_id)
        except DoesNotExist:
            abort(404)
        query = query & (Payment.account == account_id)

    payments = Payment.select().where(query).order_by(-Payment.date)
    return [stringify(payment) for payment in payments]


