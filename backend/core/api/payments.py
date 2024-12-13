from flask import abort, Blueprint, request, g

from backend.core.service.payment_service import PaymentService
from backend.core.util import stringify, parse_boolean
from peewee import DoesNotExist

payments = Blueprint("payments", __name__, url_prefix="/api/payments")


@payments.get("")
def get_payments(payment_service: PaymentService):
    try:
        account_str = request.args.get("account")
        account_id = None if not account_str else int(account_str)
        processed = parse_boolean(request.args.get("processed"))
    except (ValueError, TypeError):
        abort(400)

    payments = payment_service.get_payments(g.user, account_id, processed)
    return [stringify(payment) for payment in payments]


@payments.post("/<payment_id>/process")
def process_payment(payment_id, payment_service: PaymentService):
    try:
        transactions = request.args.get("transactions")
        transactions = None if not transactions else [int(n) for n in transactions.split(",")]
    except (ValueError, TypeError):
        abort(400)

    try:
        payment_service.process_payment(g.user, payment_id, transactions)
    except DoesNotExist:
        abort(404)

    return "", 204


@payments.post("/<payment_id>/unprocess")
def unprocess_payment(payment_id, payment_service: PaymentService):
    payment_service.unprocess_payment(g.user, payment_id)
    return "", 204
