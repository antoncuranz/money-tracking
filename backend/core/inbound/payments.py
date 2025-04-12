import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import SQLModel, Session

from auth import get_current_user
from core.business.payment_service import PaymentService
from models import User, get_session

router = APIRouter(prefix="/api/payments", tags=["Payments"])

class ExchangePaymentTO(SQLModel):
    exchange_id: int
    payment_id: int
    amount: int

class PaymentTO(SQLModel):
    id: int | None
    account_id: int
    import_id: str | None
    actual_id: str | None
    date: datetime.date
    counterparty: str
    description: str
    category: str | None
    amount_usd: int
    amount_eur_with_fx: int | None
    amount_eur_without_fx: int | None
    status: int
    exchanges: List[ExchangePaymentTO]


@router.get("", response_model=List[PaymentTO])
def get_payments(user: Annotated[User, Depends(get_current_user)],
                 session: Annotated[Session, Depends(get_session)],
                 payment_service: Annotated[PaymentService, Depends()],
                 account: int | None = None, processed: bool | None = None):
    return payment_service.get_payments(session, user, account, processed)


@router.post("/{payment_id}/process", status_code=status.HTTP_204_NO_CONTENT)
def process_payment(user: Annotated[User, Depends(get_current_user)],
                    session: Annotated[Session, Depends(get_session)],
                    payment_service: Annotated[PaymentService, Depends()],
                    payment_id: int, transactions: str | None = None):
    try:
        transactions = None if not transactions else [int(n) for n in transactions.split(",")]
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    payment_service.process_payment(session, user, payment_id, transactions)


@router.post("/{payment_id}/unprocess", status_code=status.HTTP_204_NO_CONTENT)
def unprocess_payment(user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)],
                      payment_service: Annotated[PaymentService, Depends()],
                      payment_id: int):
    payment_service.unprocess_payment(session, user, payment_id)
