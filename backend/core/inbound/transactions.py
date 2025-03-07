from typing import Annotated

from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from backend.core.business.transaction_service import TransactionService
from backend.core.util import stringify
from backend.exchangerate.facade import ExchangeRateFacade
from backend.models import Transaction, User

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

def map_transaction(transaction: Transaction, exchangerate: ExchangeRateFacade):
    dict = stringify(transaction)
    dict["guessed_amount_eur"] = exchangerate.guess_amount_eur(transaction)
    return dict

@router.get("")
def get_transactions(user: Annotated[User, Depends(get_current_user)],
                     transaction_service: Annotated[TransactionService, Depends()],
                     exchangerate: Annotated[ExchangeRateFacade, Depends()],
                     account: int | None = None, paid: bool | None = None):

    transactions = transaction_service.get_transactions(user, account, paid)
    return [map_transaction(tx, exchangerate) for tx in transactions]


@router.put("/{tx_id}")
def update_transaction(user: Annotated[User, Depends(get_current_user)],
                       transaction_service: Annotated[TransactionService, Depends()],
                       tx_id: int, amount_eur: int | None = None):
    transaction_service.update_transaction(user, tx_id, amount_eur)
