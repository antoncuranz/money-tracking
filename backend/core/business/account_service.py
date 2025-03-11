from typing import Annotated, List

from fastapi import Depends, HTTPException
from sqlmodel import Session, SQLModel

from core.dataaccess.store import Store
from models import User, Account, BankAccount


class CreateAccount(SQLModel):
    name: str
    institution: str
    due_day: int | None
    autopay_offset: int | None
    icon: str | None
    color: str | None
    target_spend: int | None
    bank_account_id: int | None
    plaid_account_id: int | None
    actual_id: str | None


class CreateBankAccount(SQLModel):
    name: str
    institution: str
    icon: str | None
    plaid_account_id: int | None


class AccountService:
    def __init__(self, store: Annotated[Store, Depends()]):
        self.store = store

    def get_accounts(self, session: Session, user: User) -> List[Account]:
        if user.super_user:
            return self.store.get_all_accounts(session)
        else:
            return self.store.get_accounts_of_user(session, user)
    
    def create_account(self, session: Session, user: User, create_account: CreateAccount) -> Account:
        account = self.store.create_account(session, user, bank_account_id=create_account.bank_account_id,
                          actual_id=create_account.actual_id, plaid_account_id=create_account.plaid_account_id,
                          name=create_account.name, institution=create_account.institution,
                          due_day=create_account.due_day, autopay_offset=create_account.autopay_offset,
                          icon=create_account.icon, color=create_account.color, target_spend=create_account.target_spend)
        session.commit()
        return account
    
    def modify_account(self, session: Session, user: User, account_id: int, create_account: CreateAccount):
        account = self.store.get_account(session, user, account_id)
        if not account:
            raise HTTPException(404)
        
        account.name = create_account.name
        account.institution = create_account.institution
        account.due_day = create_account.due_day
        account.autopay_offset = create_account.autopay_offset
        account.icon = create_account.icon
        account.color = create_account.color
        account.target_spend = create_account.target_spend
        account.bank_account_id = create_account.bank_account_id
        account.plaid_account_id = create_account.plaid_account_id
        account.actual_id = create_account.actual_id
        session.commit()

    def get_bank_accounts(self, session: Session, user: User) -> List[BankAccount]:
        if user.super_user:
            return self.store.get_all_bank_accounts(session)
        else:
            return self.store.get_bank_accounts_of_user(session, user)
    
    def create_bank_account(self, session: Session, user: User, create_bank_account: CreateBankAccount) -> BankAccount:
        bank_account = self.store.create_bank_account(session, user, name=create_bank_account.name,
                                                      institution=create_bank_account.institution,
                                                      icon=create_bank_account.icon,
                                                      plaid_account_id=create_bank_account.plaid_account_id)
        session.commit()
        return bank_account

    def modify_bank_account(self, session: Session, user: User, bank_account_id: int, create_bank_account: CreateBankAccount):
        bank_account = self.store.get_bank_account(session, user, bank_account_id)
        if not bank_account:
            raise HTTPException(404)
        
        bank_account.name = create_bank_account.name
        bank_account.institution = create_bank_account.institution
        bank_account.icon = create_bank_account.icon
        bank_account.plaid_account_id = create_bank_account.plaid_account_id
        session.commit()
