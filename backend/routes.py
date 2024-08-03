from flask import abort, Blueprint, request

from backend.clients.teller import TellerClient
from backend.models import *
from backend.service.actual_service import ActualService
from backend.service.balance_service import BalanceService
from backend.service.conversion_service import ConversionService
from backend.service.transaction_service import TransactionService

api = Blueprint("api", __name__)


@api.get("/api/accounts")
def get_accounts():
    return list(Account.select().dicts())


@api.get("/api/accounts/<account_id>/balances")
def get_balances(account_id, teller: TellerClient):
    return teller.get_account_balances(account_id).json()


@api.get("/api/accounts/<account_id>/transactions")
def get_transactions(account_id):
    return list(Transaction.select().where(Transaction.account == account_id).order_by(-Transaction.date).dicts())


@api.get("/api/accounts/<account_id>/credits")
def get_credits(account_id):
    query = Credit.select(Credit, CreditTransaction) \
        .left_outer_join(CreditTransaction) \
        .where(Credit.account == account_id).order_by(-Credit.date).dicts()

    credits = {}
    for result in query:
        id = result["id"]
        if id not in credits:
            credits[id] = result
            credits[id]["transactions"] = []

        if result["transaction"] is not None:
            credits[id]["transactions"].append(result["transaction"])

    return list(credits.values())


@api.put("/api/accounts/<account_id>/credits/<credit_id>")
def update_credit(account_id, credit_id, balance_service: BalanceService):
    try:
        amount = int(request.args.get("amount"))
        transaction_id = int(request.args.get("transaction"))

        Transaction.get(
            (Transaction.id == transaction_id) &
            (Transaction.account == account_id) &
            (Transaction.status != Transaction.Status.PENDING.value) &
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

    if balance_service.calc_credit_remaining(credit) < amount:
        raise Exception(f"Error: Credit {credit_id} has not enough balance!")

    model, created = CreditTransaction.get_or_create(
        credit_id=credit_id,
        transaction_id=transaction_id,
        defaults={"amount": amount}
    )

    if not created:
        model.amount = amount
        model.save()

    return "", 204


@api.get("/api/accounts/<account_id>/payments")
def get_payments(account_id):
    return list(Payment.select().where(Payment.account == account_id).order_by(-Payment.date).dicts())


@api.get("/api/balance/total")
def get_balance_total(balance_service: BalanceService):
    balance = Transaction.select(fn.SUM(Transaction.amount_usd)) \
        .where(Transaction.status != Transaction.Status.PAID.value).scalar()

    balance -= balance_service.calc_balance_exchanged()
    return str(balance), 200


@api.get("/api/balance/posted")
def get_balance_posted():
    balance = Transaction.select(fn.SUM(Transaction.amount_usd)).where(
        (Transaction.status == Transaction.Status.POSTED.value) |
        (Transaction.status == Transaction.Status.IMPORTED.value)
    ).scalar()
    return str(balance), 200


@api.get("/api/balance/pending")
def get_balance_pending():
    balance = Transaction.select(fn.SUM(Transaction.amount_usd)) \
        .where(Transaction.status == Transaction.Status.PENDING.value).scalar()
    return str(balance), 200


@api.get("/api/balance/exchanged")
def get_balance_exchanged(balance_service: BalanceService):
    balance = balance_service.calc_balance_exchanged()
    return str(balance), 200


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


@api.post("/api/import/<account_id>")
def import_transactions(account_id, transaction_service: TransactionService, conversion_service: ConversionService):
    try:
        account = Account.get(Account.id == account_id)
    except DoesNotExist:
        abort(404)

    access_token = request.args.get("access_token")
    if access_token is not None:
        account.teller_access_token = access_token
        account.save()

    try:
        transaction_service.import_transactions(account)
    except TransactionService.MfaRequiredException:
        return "", 418

    conversion_service.add_missing_eur_amounts(account)

    return "", 204


@api.post("/api/actual/<account_id>")
def import_transactions_to_actual(account_id, actual_service: ActualService):
    try:
        account = Account.get(Account.id == account_id)
    except DoesNotExist:
        abort(404)

    actual_service.import_transactions(account)

    return "", 204
