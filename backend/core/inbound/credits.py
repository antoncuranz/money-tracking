import datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlmodel import SQLModel, Session

from backend.auth import get_current_user
from backend.core.business.credit_service import CreditService
from backend.core.inbound.transactions import CreditTransactionTO

from backend.models import User, get_session

router = APIRouter(prefix="/api/credits", tags=["Credits"])


class CreditTO(SQLModel):
    id: int | None
    account_id: int
    import_id: str
    date: datetime.date
    counterparty: str
    description: str
    category: str | None
    amount_usd: int
    transactions: List[CreditTransactionTO]


@router.get("", response_model=List[CreditTO])
def get_credits(user: Annotated[User, Depends(get_current_user)],
                session: Annotated[Session, Depends(get_session)],
                credit_service: Annotated[CreditService, Depends()],
                account: int | None = None, usable: bool | None = None):
    return credit_service.get_credits(session, user, account, usable)


@router.put("/{credit_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_credit(user: Annotated[User, Depends(get_current_user)],
                  session: Annotated[Session, Depends(get_session)],
                  credit_service: Annotated[CreditService, Depends()],
                  credit_id: int, amount: int, transaction: int):
    credit_service.update_credit(session, user, credit_id, transaction, amount)
