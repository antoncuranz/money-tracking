from flask import Blueprint, g

from backend.core.service.account_service import AccountService

accounts = Blueprint("accounts", __name__, url_prefix="/api/accounts")


@accounts.get("")
def get_accounts(account_service: AccountService):
    accounts = account_service.get_accounts_of_user(g.user)
    return list(accounts.dicts())

