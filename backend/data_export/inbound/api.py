from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from auth import get_current_user
from data_export.facade import DataExportFacade
from models import User, get_session

router = APIRouter(prefix="/api/export", tags=["Data Export"])


@router.post("/actual/{account_id}", status_code=status.HTTP_201_CREATED)
def export_transactions_to_actual(user: Annotated[User, Depends(get_current_user)],
                                  session: Annotated[Session, Depends(get_session)],
                                  data_export: Annotated[DataExportFacade, Depends()],
                                  account_id: int):
    # TODO: consider super_user status
    data_export.export_transactions(session, user, account_id)
    data_export.update_transactions(session, user, account_id)
