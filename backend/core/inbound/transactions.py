import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlmodel import SQLModel, Session

from auth import get_current_user
from core.business.transaction_service import TransactionService
from models import User, get_session

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

class CreditTransactionTO(SQLModel):
    credit_id: int
    transaction_id: int
    amount: int
    
class TransactionTO(SQLModel):
    id: int
    account_id: int
    payment_id: int | None
    import_id: str
    actual_id: str | None
    date: datetime.date
    counterparty: str
    description: str
    category: str | None
    amount_usd: int
    amount_eur: int | None
    status: int
    fees_and_risk_eur: int | None
    ignore: bool | None
    guessed_amount_eur: int | None
    credits: List[CreditTransactionTO]

@router.get("", response_model=List[TransactionTO])
def get_transactions(user: Annotated[User, Depends(get_current_user)],
                     session: Annotated[Session, Depends(get_session)],
                     transaction_service: Annotated[TransactionService, Depends()],
                     account: int | None = None, paid: bool | None = None):
    return transaction_service.get_transactions_with_guessed_amount(session, user, account, paid)


@router.put("/{tx_id}")
def update_transaction(user: Annotated[User, Depends(get_current_user)],
                       session: Annotated[Session, Depends(get_session)],
                       transaction_service: Annotated[TransactionService, Depends()],
                       tx_id: int, amount_eur: int | None = None):
    transaction_service.update_transaction(session, user, tx_id, amount_eur)
