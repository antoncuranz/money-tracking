from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth import get_current_user
from backend.core.business.credit_service import CreditServiceDep
from backend.core.util import stringify
from peewee import DoesNotExist

from backend.models import User

router = APIRouter(prefix="/api/credits", tags=["Credits"])


@router.get("")
def get_credits(user: Annotated[User, Depends(get_current_user)],
                credit_service: CreditServiceDep,
                account: int | None = None, usable: bool | None = None):
    
    credits = credit_service.get_credits(user, account, usable)
    return [stringify(credit) for credit in credits]


@router.put("/{credit_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_credit(user: Annotated[User, Depends(get_current_user)],
                  credit_service: CreditServiceDep,
                  credit_id: int, amount: int, transaction: int):
    try:
        credit_service.update_credit(user, credit_id, transaction, amount)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
