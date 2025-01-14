from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth import get_current_user
from backend.data_import.business.import_service import ImportServiceDep
from backend.models import *

router = APIRouter(prefix="/api/import", tags=["Data Import"])


@router.post("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def import_transactions(user: Annotated[User, Depends(get_current_user)],
                        import_service: ImportServiceDep,
                        account_id: int):
    try:
        import_service.import_transactions(user, account_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def import_transactions_all_accounts(import_service: ImportServiceDep):
    import_service.import_transactions_all_accounts()
