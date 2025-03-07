from typing import Annotated, List

from fastapi import Depends

from backend.core.dataaccess.account_repository import AccountRepository
from backend.models import User, Account, BankAccount


class AccountService:
    def __init__(self, account_repository: Annotated[AccountRepository, Depends()]):
        self.account_repository = account_repository

    def get_accounts_of_user(self, user: User) -> List[Account]:
        return self.account_repository.get_accounts_of_user(user)

    def get_bank_accounts_of_user(self, user: User) -> List[BankAccount]:
        return self.account_repository.get_bank_accounts_of_user(user)
