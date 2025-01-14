from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth import get_current_user
from backend.core.service.transaction_service import TransactionServiceDep
from backend.core.util import stringify
from backend.models import Transaction, User
from peewee import DoesNotExist

from backend.core.service.exchange_service import ExchangeService, ExchangeServiceDep

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

def map_transaction(transaction: Transaction, exchange_service: ExchangeService):
    dict = stringify(transaction)
    dict["guessed_amount_eur"] = exchange_service.guess_amount_eur(transaction)
    return dict

@router.get("")
def get_transactions(user: Annotated[User, Depends(get_current_user)],
                     transaction_service: TransactionServiceDep,
                     exchange_service: ExchangeServiceDep,
                     account: int | None = None, paid: bool | None = None):

    transactions = transaction_service.get_transactions(user, account, paid)
    return [map_transaction(tx, exchange_service) for tx in transactions]


@router.put("/{tx_id}")
def update_transaction(user: Annotated[User, Depends(get_current_user)],
                       transaction_service: TransactionServiceDep,
                       tx_id: int, amount_eur: int | None = None):
    try:
        transaction_service.update_transaction(user, tx_id, amount_eur)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
