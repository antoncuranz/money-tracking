from datetime import datetime
from decimal import Decimal
from typing import Annotated, Dict

from fastapi import APIRouter, Depends
from sqlmodel import Session, SQLModel

from auth import require_super_user, get_current_user
from core.business.balance_service import BalanceService
from models import User, get_session

router = APIRouter(prefix="/api/balance", tags=["Balances"])


class BalancesTO(SQLModel):
    total: int
    posted: int
    pending: int
    credits: int
    exchanged: int
    virtual_account: int
    avg_exchange_rate: Decimal


@router.get("", response_model=BalancesTO)
def get_balances(_: Annotated[None, Depends(require_super_user)],
                 session: Annotated[Session, Depends(get_session)],
                 balance_service: Annotated[BalanceService, Depends()]):
    posted = balance_service.get_balance_posted(session)
    pending = balance_service.get_balance_pending(session)
    credits = balance_service.get_balance_credits(session)
    exchanged = balance_service.calc_balance_exchanged(session)
    total = posted + pending - credits - exchanged

    return BalancesTO(
        total=total,
        posted=posted,
        pending=pending,
        credits=credits,
        exchanged=exchanged,
        virtual_account=balance_service.get_virtual_account_balance(session),
        avg_exchange_rate=balance_service.get_avg_exchange_rate(session)
    )


class AccountBalanceTO(SQLModel):
    posted: int
    pending: int
    total_spent: int
    total_credits: int
    last_successful_update: datetime | None


@router.get("/accounts", response_model=Dict[int, AccountBalanceTO])
def get_account_balances(user: Annotated[User, Depends(get_current_user)],
                         session: Annotated[Session, Depends(get_session)],
                         balance_service: Annotated[BalanceService, Depends()]):
    return balance_service.get_account_balances(session, user)


class FeeSummaryTO(SQLModel):
    fees_and_risk_eur: int


@router.get("/fees", response_model=FeeSummaryTO)
def get_fee_summary(_: Annotated[None, Depends(require_super_user)],
                    session: Annotated[Session, Depends(get_session)],
                    balance_service: Annotated[BalanceService, Depends()]):
    return FeeSummaryTO(
        fees_and_risk_eur=balance_service.get_fees_and_risk_eur(session)
    )
