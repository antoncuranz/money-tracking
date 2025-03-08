from typing import Annotated, List

from fastapi import Depends
from sqlmodel import Session

from core.dataaccess.store import Store
from models import User, Account, BankAccount, engine


class AccountService:
    def __init__(self, store: Annotated[Store, Depends()]):
        self.store = store

    def get_accounts_of_user(self, session: Session, user: User) -> List[Account]:
        return self.store.get_accounts_of_user(session, user)

    def get_bank_accounts_of_user(self, session: Session, user: User) -> List[BankAccount]:
        return self.store.get_bank_accounts_of_user(session, user)
