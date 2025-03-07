from typing import List

from backend.models import Account, User


class DatesRepository:
    def get_accounts_of_user(self, user: User) -> List[Account]:
        return Account.select().where(Account.user == user.id).order_by(Account.id)
