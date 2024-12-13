from flask import abort, Blueprint, g, request

from backend.models import *
from backend.data_export.actual_service import ActualService

api = Blueprint("api", __name__)

@api.before_app_request
def extract_username():
    username = request.headers.get("X-Auth-Request-Preferred-Username")
    if not username:
        abort(401, description="Unauthorized: Username is required.")

    try:
        g.user = User.get(User.name == username)
    except DoesNotExist:
        abort(401, description="Unauthorized: User not found in database.")


# TODO: move to other blueprints


@api.get("/api/fee_summary")
def get_fee_summary(): # TODO: user
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
    for account in Account.select().where(Account.user == g.user.id):
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
        account = Account.get((Account.user == g.user.id) & (Account.id == account_id))
    except DoesNotExist:
        abort(404)

    # TODO: consider super_user status
    actual_service.export_transactions(account)
    actual_service.update_transactions(account)

    return "", 204


