from flask import abort, Blueprint, request

from backend.api.util import stringify
from backend.models import *
from backend.service.balance_service import BalanceService

credits = Blueprint("credits", __name__)


@credits.get("/api/accounts/<account_id>/credits")
def get_credits(account_id):
    query = Credit.select().where(Credit.account == account_id).order_by(-Credit.date)
    return [stringify(credit) for credit in query]


@credits.put("/api/accounts/<account_id>/credits/<credit_id>")
def update_credit(account_id, credit_id, balance_service: BalanceService):
    try:
        amount = int(request.args.get("amount"))
        transaction_id = int(request.args.get("transaction"))

        tx = Transaction.get(
            (Transaction.id == transaction_id) &
            (Transaction.account == account_id) &
            (Transaction.status != Transaction.Status.PAID.value)
        )
        credit = Credit.get((Credit.id == credit_id) & (Credit.account == account_id))
    except DoesNotExist:
        abort(404)
    except (ValueError, TypeError):
        abort(400)

    if amount == 0:
        CreditTransaction.delete().where(
            (CreditTransaction.credit == credit_id) &
            (CreditTransaction.transaction == transaction_id)
        ).execute()
        return "", 204

    ct = CreditTransaction.get_or_none(credit=credit, transaction=tx)
    current_amount = 0 if not ct else ct.amount

    if balance_service.calc_credit_remaining(credit) + current_amount < amount:
        raise Exception(f"Error: Credit {credit_id} has not enough balance!")

    if balance_service.calc_transaction_remaining(tx) + current_amount < amount:
        raise Exception(f"Error: Transaction {transaction_id} has not enough balance!")

    model, created = CreditTransaction.get_or_create(
        credit_id=credit_id,
        transaction_id=transaction_id,
        defaults={"amount": amount}
    )

    if not created:
        model.amount = amount
        model.save()

    return "", 204
