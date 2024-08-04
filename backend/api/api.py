from flask import abort, Blueprint, request

from backend.models import *
from backend.service.actual_service import ActualService
from backend.service.payment_service import PaymentService

api = Blueprint("api", __name__)
# TODO: move to other blueprints


@api.put("/api/accounts/<account_id>/transactions/<tx_id>")
def update_transaction(account_id, tx_id):
    try:
        amount_eur_str = request.args.get("amount_eur")
        amount_eur = None if not amount_eur_str else int(amount_eur_str)
        transaction = Transaction.get((Transaction.id == tx_id) & (Transaction.account == account_id))
    except DoesNotExist:
        abort(404)
    except (ValueError, TypeError):
        abort(400)

    transaction.amount_eur = amount_eur
    transaction.save()

    return "", 200


@api.post("/api/actual/<account_id>")
def import_transactions_to_actual(account_id, actual_service: ActualService):
    try:
        account = Account.get(Account.id == account_id)
    except DoesNotExist:
        abort(404)

    actual_service.import_transactions(account)

    return "", 204


@api.post("/api/accounts/<account_id>/payments/<payment_id>")
def process_payment(account_id, payment_id, payment_service: PaymentService):
    try:
        # transactions = request.args.get("transactions")
        # transactions = [] if not transactions else [int(n) for n in transactions.split(",")]
        payment = Payment.get(
            (Payment.id == payment_id) &
            (Payment.account == account_id)
        )
    except DoesNotExist:
        abort(404)
    except (ValueError, TypeError):
        abort(400)

    payment_service.process_payment_auto(payment)

    return "not yet implemented", 555
