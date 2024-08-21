from flask import abort, Blueprint

from backend.clients.actual import IActualClient
from backend.models import *
from backend.service.actual_service import ActualService
from backend.service.payment_service import PaymentService

api = Blueprint("api", __name__)


# TODO: move to other blueprints


@api.get("/api/fee_summary")
def get_fee_summary():
    query = Transaction.select(fn.SUM(Transaction.fx_fees), fn.SUM(Transaction.ccy_risk)) \
            .where(Transaction.status == Transaction.Status.PAID.value)[0]

    return {  # TODO: not working
        "fx_fees": query.fx_fees,
        "ccy_risk": query.ccy_risk
    }


@api.post("/api/actual/<account_id>")
def import_transactions_to_actual(account_id, actual_service: ActualService):
    try:
        account = Account.get(Account.id == account_id)
    except DoesNotExist:
        abort(404)

    actual_service.import_transactions(account)

    return "", 204


@api.post("/api/accounts/<account_id>/payments/<payment_id>")
def process_payment(account_id, payment_id, payment_service: PaymentService, actual_service: ActualService):
    try:
        # transactions = request.args.get("transactions")
        # transactions = [] if not transactions else [int(n) for n in transactions.split(",")]
        payment = Payment.get(
            (Payment.id == payment_id) &
            (Payment.account == account_id)
        )
        account = Account.get(Account.id == account_id)
    except DoesNotExist:
        abort(404)
    except (ValueError, TypeError):
        abort(400)

    processed_transactions = payment_service.process_payment_auto(payment)
    actual_service.update_transactions(account, processed_transactions)
    actual_service.import_payment(account, payment)

    return "", 204


@api.delete("/api/accounts/<account_id>/payments/<payment_id>")
def unprocess_payment(account_id, payment_id, actual_service: ActualService, actual: IActualClient):
    try:
        payment = Payment.get(
            (Payment.id == payment_id) &
            (Payment.account == account_id)
        )
        account = Account.get(Account.id == account_id)
    except DoesNotExist:
        abort(404)
    except (ValueError, TypeError):
        abort(400)

    transactions = Transaction.select().where(
        (Transaction.payment == payment_id) &
        (Transaction.status == Transaction.Status.PAID.value)
    )
    for tx in transactions:
        tx.status_enum = Transaction.Status.POSTED
        tx.payment = None
        tx.fx_fees = None
        tx.ccy_risk = None
        tx.save()

    payment_actual_id = payment.actual_id

    payment.processed = False
    payment.amount_eur = None
    payment.actual_id = None
    payment.save()

    actual_service.update_transactions(account, transactions)
    if payment_actual_id is not None:
        actual.delete_transaction(payment_actual_id)

    return "", 204
