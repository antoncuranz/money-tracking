from backend.models import Account
from flask_injector import inject


class AccountService:

    @inject
    def __init__(self):
        pass

    def get_accounts_of_user(self, user):
        return Account.select().where(Account.user == user.id).order_by(Account.id)