from typing import Annotated

from sqlmodel import Session
from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from backend.core.business.account_service import AccountService
from backend.models import User, get_session

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


@router.get("")
def get_accounts(user: Annotated[User, Depends(get_current_user)],
                 session: Annotated[Session, Depends(get_session)],
                 account_service: Annotated[AccountService, Depends()]):
    return account_service.get_accounts_of_user(session, user)

