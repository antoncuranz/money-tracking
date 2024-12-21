from flask import Blueprint, g

from backend.core.service.account_service import AccountService

bank_accounts = Blueprint("bank_accounts", __name__, url_prefix="/api/bank_accounts")


@bank_accounts.get("")
def get_bank_accounts(account_service: AccountService):
    bank_accounts = account_service.get_bank_accounts_of_user(g.user)
    return list(bank_accounts.dicts())

