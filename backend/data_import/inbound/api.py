from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from auth import get_current_user
from data_import.business.import_service import ImportService
from models import User, get_session

router = APIRouter(prefix="/api/import", tags=["Data Import"])


@router.post("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def import_transactions(user: Annotated[User, Depends(get_current_user)],
                        session: Annotated[Session, Depends(get_session)],
                        import_service: Annotated[ImportService, Depends()],
                        account_id: int):
    import_service.import_transactions(session, user, account_id)

@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def import_transactions_all_accounts(session: Annotated[Session, Depends(get_session)],
                                     import_service: Annotated[ImportService, Depends()]):
    import_service.import_transactions_all_accounts(session)
