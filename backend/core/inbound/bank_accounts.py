from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from auth import get_current_user
from core.business.account_service import AccountService, CreateBankAccount, BankAccountTO
from models import User, get_session

router = APIRouter(prefix="/api/bank_accounts", tags=["Bank Accounts"])


@router.get("", response_model=List[BankAccountTO])
def get_bank_accounts(user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)],
                      account_service: Annotated[AccountService, Depends()]):
    return account_service.get_bank_accounts(session, user)

@router.post("", response_model=BankAccountTO)
def create_bank_account(user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)],
                   account_service: Annotated[AccountService, Depends()],
                   create_bank_account: CreateBankAccount):
    return account_service.create_bank_account(session, user, create_bank_account)

@router.put("/{bank_account_id}", status_code=status.HTTP_204_NO_CONTENT)
def modify_account(user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)],
                   account_service: Annotated[AccountService, Depends()],
                   bank_account_id: int,
                   create_account: CreateBankAccount):
    account_service.modify_bank_account(session, user, bank_account_id, create_account)
