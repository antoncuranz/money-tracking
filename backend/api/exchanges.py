from decimal import Decimal

from flask import abort, Blueprint, request

from backend.api.util import stringify, parse_boolean
from backend.models import *
from backend.service.balance_service import BalanceService

exchanges = Blueprint("exchanges", __name__, url_prefix="/api/exchanges")


@exchanges.get("")
def get_exchanges():
    try:
        usable = parse_boolean(request.args.get("usable"))
    except (ValueError, TypeError):
        abort(400)

    query = True
    if usable is True:
        query = query & (Exchange.amount_usd > fn.COALESCE(
            ExchangePayment.select(fn.SUM(ExchangePayment.amount)).join(Payment)
            .where((ExchangePayment.exchange == Exchange.id) & (Payment.processed == True)), 0
        ))

    exchanges = Exchange.select().where(query).order_by(-Exchange.date)
    return [stringify(exchange, extra_attrs=[]) for exchange in exchanges]


@exchanges.post("")
def post_exchange():
    json = request.json

    exchange_rate = Decimal(json["exchange_rate"]) / 10000000
    amount_eur = round(Decimal(json["amount_usd"]) / exchange_rate)
    fees_eur = json["paid_eur"] - amount_eur

    model = Exchange.create(
        date=json["date"], amount_usd=json["amount_usd"], exchange_rate=exchange_rate, amount_eur=amount_eur,
        paid_eur=json["paid_eur"], fees_eur=fees_eur)
    return str(model.id), 200


@exchanges.delete("/<exchange_id>")
def delete_exchange(exchange_id):
    try:
        exchange = Exchange.get(Exchange.id == exchange_id)
    except DoesNotExist:
        abort(404)

    if not ExchangePayment.select().where(ExchangePayment.exchange == exchange_id):
        exchange.delete_instance()
        return "", 204
    else:
        return "Exchange is still in use", 500


@exchanges.put("/<exchange_id>")
def update_exchange(exchange_id, balance_service: BalanceService):
    try:
        amount = int(request.args.get("amount"))
        payment_id = int(request.args.get("payment"))

        payment = Payment.get(
            (Payment.id == payment_id) &
            (Payment.processed == False)
        )
        exchange = Exchange.get(Exchange.id == exchange_id)
    except DoesNotExist:
        abort(404)
    except (ValueError, TypeError):
        abort(400)

    if amount == 0:
        ExchangePayment.delete().where(
            (ExchangePayment.exchange == exchange_id) &
            (ExchangePayment.payment == payment_id)
        ).execute()
        return "", 204

    ep = ExchangePayment.get_or_none(exchange=exchange, payment=payment)
    current_amount = 0 if not ep else ep.amount

    if balance_service.calc_exchange_remaining(exchange) + current_amount < amount:
        raise Exception(f"Error: Exchange {exchange_id} has not enough balance!")

    if balance_service.calc_payment_remaining(payment) + current_amount < amount:
        raise Exception(f"Error: Exchange {exchange_id} has not enough balance!")

    model, created = ExchangePayment.get_or_create(
        exchange_id=exchange_id,
        payment_id=payment_id,
        defaults={"amount": amount}
    )

    if not created:
        model.amount = amount
        model.save()

    return "", 204
