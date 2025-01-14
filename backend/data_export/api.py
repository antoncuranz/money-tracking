from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth import get_current_user
from backend.data_export.actual_service import ActualServiceDep
from backend.models import *

router = APIRouter(prefix="/api/export", tags=["Data Export"])


@router.post("/actual/{account_id}", status_code=status.HTTP_201_CREATED)
def export_transactions_to_actual(user: Annotated[User, Depends(get_current_user)],
                                  actual_service: ActualServiceDep,
                                  account_id: int):
    try:
        account = Account.get((Account.user == user.id) & (Account.id == account_id))
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # TODO: consider super_user status
    actual_service.export_transactions(account)
    actual_service.update_transactions(account)
