from flask import abort, Blueprint, g

from backend import ActualService
from backend.models import *

data_export = Blueprint("export", __name__, url_prefix="/api/export")


@data_export.post("/actual/<account_id>")
def export_transactions_to_actual(account_id, actual_service: ActualService):
    try:
        account = Account.get((Account.user == g.user.id) & (Account.id == account_id))
    except DoesNotExist:
        abort(404)

    # TODO: consider super_user status
    actual_service.export_transactions(account)
    actual_service.update_transactions(account)

    return "", 204
