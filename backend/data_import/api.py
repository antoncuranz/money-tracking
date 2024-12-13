from flask import abort, Blueprint, request, g

from backend.data_import.import_service import ImportService
from backend.data_import.teller_client import TellerMfaRequired
from backend.models import *

data_import = Blueprint("import", __name__, url_prefix="/api/import")


@data_import.post("/<account_id>")
def import_transactions(account_id, import_service: ImportService):
    access_token = request.args.get("access_token")
    enrollment = request.args.get("enrollment_id")

    try:
        import_service.import_transactions(g.user, account_id, access_token, enrollment)
    except DoesNotExist:
        abort(404)
    except TellerMfaRequired:
        abort(418, description="Teller interaction required")

    return "", 204

@data_import.post("")
def import_transactions_all_accounts(import_service: ImportService):
    import_service.import_transactions_all_accounts()
    return "", 204
