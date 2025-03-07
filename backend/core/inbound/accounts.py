from typing import Annotated

from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from backend.core.business.account_service import AccountService
from backend.models import User

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


@router.get("")
def get_accounts(user: Annotated[User, Depends(get_current_user)],
                 account_service: Annotated[AccountService, Depends()]):
    accounts = account_service.get_accounts_of_user(user)
    return list(accounts.dicts())

