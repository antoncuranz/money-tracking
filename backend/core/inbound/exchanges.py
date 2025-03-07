from typing import Annotated

from fastapi import APIRouter, Depends, status

from backend.auth import require_super_user
from backend.core.business.exchange_service import CreateExchange, ExchangeService
from backend.core.util import stringify

router = APIRouter(prefix="/api/exchanges", tags=["Exchanges"], dependencies=[Depends(require_super_user)])


@router.get("")
def get_exchanges(exchange_service: Annotated[ExchangeService, Depends()], usable: bool | None = None):
    exchanges = exchange_service.get_exchanges(usable)
    return [stringify(exchange, extra_attrs=[]) for exchange in exchanges]


@router.post("")
def post_exchange(exchange_service: Annotated[ExchangeService, Depends()], exchange: CreateExchange):
    model = exchange_service.create_exchange(exchange)
    return str(model.id)


@router.delete("/{exchange_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exchange(exchange_service: Annotated[ExchangeService, Depends()], exchange_id: int):
    exchange_service.delete_exchange(exchange_id)


@router.put("/{exchange_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_exchange(exchange_service: Annotated[ExchangeService, Depends()], exchange_id: int, amount: int, payment: int):
    exchange_service.update_exchange(exchange_id, amount, payment)
