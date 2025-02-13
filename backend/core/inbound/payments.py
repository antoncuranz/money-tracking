from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.business.payment_service import PaymentServiceDep
from backend.core.util import stringify
from backend.models import User
from backend.auth import get_current_user
from peewee import DoesNotExist

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.get("")
def get_payments(user: Annotated[User, Depends(get_current_user)],
                 payment_service: PaymentServiceDep,
                 account: int | None = None, processed: bool | None = None):
    
    payments = payment_service.get_payments(user, account, processed)
    return [stringify(payment) for payment in payments]


@router.post("/{payment_id}/process", status_code=status.HTTP_204_NO_CONTENT)
def process_payment(user: Annotated[User, Depends(get_current_user)],
                    payment_service: PaymentServiceDep,
                    payment_id: int, transactions: str | None = None):
    try:
        transactions = None if not transactions else [int(n) for n in transactions.split(",")]
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    try:
        payment_service.process_payment(user, payment_id, transactions)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/{payment_id}/unprocess", status_code=status.HTTP_204_NO_CONTENT)
def unprocess_payment(user: Annotated[User, Depends(get_current_user)],
                      payment_service: PaymentServiceDep,
                      payment_id: int):
    payment_service.unprocess_payment(user, payment_id)
