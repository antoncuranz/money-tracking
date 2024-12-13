import json

from flask import abort, Blueprint, g

from backend.core.service.balance_service import BalanceService

balances = Blueprint("balances", __name__, url_prefix="/api/balance")


@balances.get("")
def get_balances(balance_service: BalanceService):
    if not g.user.super_user:
        abort(401)
        
    posted = balance_service.get_balance_posted()
    pending = balance_service.get_balance_pending()
    credits = balance_service.get_balance_credits()
    exchanged = balance_service.calc_balance_exchanged()
    total = posted + pending - credits - exchanged

    return json.dumps({
        "accounts": balance_service.get_account_balances(),
        "total": total,
        "posted": posted,
        "pending": pending,
        "credits": credits,
        "exchanged": exchanged,
        "virtual_account": balance_service.get_virtual_account_balance()
    })

@balances.get("/fees")
def get_fee_summary(balance_service: BalanceService):
    if not g.user.super_user:
        abort(401)
        
    return {
        "fees_and_risk_eur": balance_service.get_fees_and_risk_eur()
    }
