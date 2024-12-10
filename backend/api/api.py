from flask import abort, Blueprint, g, request

from backend.clients.actual import IActualClient
from backend.models import *
from backend.service.actual_service import ActualService
from backend.service.payment_service import PaymentService

api = Blueprint("api", __name__)

@api.before_app_request
def extract_username():
    username = request.headers.get("X-Auth-Request-Preferred-Username")
    if not username:
        abort(401, description="Unauthorized: Username is required.")

    g.username = username


# TODO: move to other blueprints


@api.get("/api/fee_summary")
def get_fee_summary():
    fees_and_risk_eur = Transaction.select(fn.SUM(Transaction.fees_and_risk_eur)) \
            .where(Transaction.status == Transaction.Status.PAID.value).scalar()

    return {
        "fees_and_risk_eur": fees_and_risk_eur
    }


@api.get("/api/dates/<year>/<month>")
def get_due_dates(year, month):
    selected_month = datetime.date(int(year), int(month), 1)

    def next_month(date):
        return (date.replace(day=1) + datetime.timedelta(days=40)).replace(day=1)
    
    def get_correct_month(due_day, offset, month):
        if due_day > offset:
            return month
        else:
            return next_month(month)

    result = {}
    for account in Account.select():
        if account.due_day is None:
            continue
        result[account.id] = dict(color=(account.color if account.color else "black"))
        
        correct_month = get_correct_month(account.due_day, 25, selected_month)
        result[account.id]["statement"] = (correct_month.replace(day=account.due_day) - datetime.timedelta(days=25)).isoformat()
        
        offset = account.autopay_offset if account.autopay_offset else 0
        correct_month = get_correct_month(account.due_day, offset, selected_month)
        result[account.id]["due"] = (correct_month.replace(day=account.due_day) - datetime.timedelta(days=offset)).isoformat()

    return result


@api.post("/api/actual/<account_id>")
def import_transactions_to_actual(account_id, actual_service: ActualService):
    try:
        account = Account.get(Account.id == account_id)
    except DoesNotExist:
        abort(404)

    actual_service.import_transactions(account)
    actual_service.update_transactions(account)

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
        tx.fees_and_risk_eur = None
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
