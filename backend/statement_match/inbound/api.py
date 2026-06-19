from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlmodel import Session

from auth import get_current_user
from models import User, get_session
from statement_match.business.statement_match_service import StatementMatchResponse, StatementMatchService

router = APIRouter(prefix="/api/statement-match", tags=["Statement Match"])


@router.post("/{account_id}", response_model=StatementMatchResponse)
def match_statement(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    statement_match_service: Annotated[StatementMatchService, Depends()],
    account_id: int,
    file: UploadFile = File(...),
):
    return statement_match_service.match_statement(session, user, account_id, file.file.read())
