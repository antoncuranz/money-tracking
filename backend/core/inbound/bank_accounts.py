from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel import Session

from auth import get_current_user
from core.business.account_service import AccountService
from models import User, get_session

router = APIRouter(prefix="/api/bank_accounts", tags=["Bank Accounts"])


@router.get("")
def get_bank_accounts(user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)],
                      account_service: Annotated[AccountService, Depends()]):
    return account_service.get_bank_accounts_of_user(session, user)

