from typing import Annotated, List

from sqlmodel import Session, SQLModel
from fastapi import APIRouter, Depends, status

from auth import get_current_user
from core.business.account_service import AccountService, CreateAccount
from core.inbound.user import UserTO
from models import User, get_session

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


class AccountTO(SQLModel):
    id: int
    user: UserTO
    bank_account_id: int | None
    actual_id: str | None
    plaid_account_id: int | None
    name: str
    institution: str
    due_day: int | None
    autopay_offset: int | None
    icon: str | None
    color: str | None
    target_spend: int | None

@router.get("", response_model=List[AccountTO])
def get_accounts(user: Annotated[User, Depends(get_current_user)],
                 session: Annotated[Session, Depends(get_session)],
                 account_service: Annotated[AccountService, Depends()]):
    return account_service.get_accounts(session, user)

@router.post("", response_model=AccountTO)
def create_account(user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)],
                   account_service: Annotated[AccountService, Depends()],
                   create_account: CreateAccount):
    return account_service.create_account(session, user, create_account)

@router.put("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def modify_account(user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)],
                   account_service: Annotated[AccountService, Depends()],
                   account_id: int,
                   create_account: CreateAccount):
    account_service.modify_account(session, user, account_id, create_account)
