from flask import abort, Blueprint, g

from backend.data_import.import_service import ImportService
from backend.models import *

data_import = Blueprint("import", __name__, url_prefix="/api/import")


@data_import.post("/<account_id>")
def import_transactions(account_id, import_service: ImportService):
    try:
        import_service.import_transactions(g.user, account_id)
    except DoesNotExist:
        abort(404)

    return "", 204

@data_import.post("")
def import_transactions_all_accounts(import_service: ImportService):
    import_service.import_transactions_all_accounts()
    return "", 204
