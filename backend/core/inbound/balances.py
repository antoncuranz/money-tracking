from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.auth import require_super_user, get_current_user
from backend.core.business.balance_service import BalanceService
from backend.models import User, get_session

router = APIRouter(prefix="/api/balance", tags=["Balances"], dependencies=[Depends(require_super_user)])


@router.get("")
def get_balances(session: Annotated[Session, Depends(get_session)],
                 balance_service: Annotated[BalanceService, Depends()]):
    posted = balance_service.get_balance_posted(session)
    pending = balance_service.get_balance_pending(session)
    credits = balance_service.get_balance_credits(session)
    exchanged = balance_service.calc_balance_exchanged(session)
    total = posted + pending - credits - exchanged
    virtual_account = balance_service.get_virtual_account_balance(session)

    return {
        "total": total,
        "posted": posted,
        "pending": pending,
        "credits": credits,
        "exchanged": exchanged,
        "virtual_account": virtual_account
    }

@router.get("/accounts")
def get_account_balances(user: Annotated[User, Depends(get_current_user)],
                         session: Annotated[Session, Depends(get_session)],
                         balance_service: Annotated[BalanceService, Depends()]):
    return balance_service.get_account_balances(session, user)

@router.get("/fees")
def get_fee_summary(session: Annotated[Session, Depends(get_session)],
                    balance_service: Annotated[BalanceService, Depends()]):
    return {
        "fees_and_risk_eur": balance_service.get_fees_and_risk_eur(session)
    }
