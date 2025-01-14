from typing import Annotated
from fastapi import Depends

from backend.models import Account, BankAccount


class AccountService:
    def get_accounts_of_user(self, user):
        return Account.select().where(Account.user == user.id).order_by(Account.id)

    def get_bank_accounts_of_user(self, user):
        return BankAccount.select().where(BankAccount.user_id == user.id).order_by(BankAccount.id)

AccountServiceDep = Annotated[AccountService, Depends()]