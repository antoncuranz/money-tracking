from flask import abort, Blueprint, request, g

from backend import ExchangeService
from backend.core.util import stringify, parse_boolean
from peewee import DoesNotExist

exchanges = Blueprint("exchanges", __name__, url_prefix="/api/exchanges")


@exchanges.get("")
def get_exchanges(exchange_service: ExchangeService):
    if not g.user.super_user:
        abort(401)
        
    try:
        usable = parse_boolean(request.args.get("usable"))
    except (ValueError, TypeError):
        abort(400)
    
    exchanges = exchange_service.get_exchanges(usable)
    return [stringify(exchange, extra_attrs=[]) for exchange in exchanges]


@exchanges.post("")
def post_exchange(exchange_service: ExchangeService):
    if not g.user.super_user:
        abort(401)
        
    model = exchange_service.create_exchange(request.json)
    return str(model.id), 200


@exchanges.delete("/<exchange_id>")
def delete_exchange(exchange_id, exchange_service: ExchangeService):
    if not g.user.super_user:
        abort(401)
        
    try:
        exchange_service.delete_exchange(exchange_id)
    except DoesNotExist:
        abort(404)
        
    return "", 204


@exchanges.put("/<exchange_id>")
def update_exchange(exchange_id, exchange_service: ExchangeService):
    if not g.user.super_user:
        abort(401)
        
    try:
        amount = int(request.args.get("amount"))
        payment_id = int(request.args.get("payment"))
    except (ValueError, TypeError):
        abort(400)

    try:
        exchange_service.update_exchange(exchange_id, amount, payment_id)
    except DoesNotExist:
        abort(404)

    return "", 204
