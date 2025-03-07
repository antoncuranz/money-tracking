from typing import Annotated, List

from fastapi import Depends

from backend.models import Account, BankAccount, User


class AccountRepository:
    def get_accounts_of_user(self, user: User) -> List[Account]:
        return Account.select().where(Account.user == user.id).order_by(Account.id)

    def get_bank_accounts_of_user(self, user: User) -> List[BankAccount]:
        return BankAccount.select().where(BankAccount.user_id == user.id).order_by(BankAccount.id)
