from typing import Annotated
from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from backend.core.business.account_service import AccountServiceDep
from backend.models import User

router = APIRouter(prefix="/api/bank_accounts", tags=["Bank Accounts"])


@router.get("")
def get_bank_accounts(user: Annotated[User, Depends(get_current_user)],
                      account_service: AccountServiceDep):
    bank_accounts = account_service.get_bank_accounts_of_user(user)
    return list(bank_accounts.dicts())

