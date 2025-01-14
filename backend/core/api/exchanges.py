from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth import require_super_user
from backend.core.service.exchange_service import ExchangeServiceDep, CreateExchange
from backend.core.util import stringify
from peewee import DoesNotExist

router = APIRouter(prefix="/api/exchanges", tags=["Exchanges"], dependencies=[Depends(require_super_user)])


@router.get("")
def get_exchanges(exchange_service: ExchangeServiceDep, usable: bool | None = None):
    exchanges = exchange_service.get_exchanges(usable)
    return [stringify(exchange, extra_attrs=[]) for exchange in exchanges]



@router.post("")
def post_exchange(exchange_service: ExchangeServiceDep, exchange: CreateExchange):
    model = exchange_service.create_exchange(exchange)
    return str(model.id)


@router.delete("/{exchange_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exchange(exchange_service: ExchangeServiceDep, exchange_id: int):
    try:
        exchange_service.delete_exchange(exchange_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.put("/{exchange_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_exchange(exchange_service: ExchangeServiceDep, exchange_id: int, amount: int, payment: int):
    try:
        exchange_service.update_exchange(exchange_id, amount, payment)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
