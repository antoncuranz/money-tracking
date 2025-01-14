import json
from fastapi import APIRouter, Depends

from backend.auth import require_super_user
from backend.core.service.balance_service import BalanceServiceDep

router = APIRouter(prefix="/api/balance", tags=["Balances"], dependencies=[Depends(require_super_user)])


@router.get("")
def get_balances(balance_service: BalanceServiceDep):
    posted = balance_service.get_balance_posted()
    pending = balance_service.get_balance_pending()
    credits = balance_service.get_balance_credits()
    exchanged = balance_service.calc_balance_exchanged()
    total = posted + pending - credits - exchanged

    return json.dumps({
        "total": total,
        "posted": posted,
        "pending": pending,
        "credits": credits,
        "exchanged": exchanged,
        "virtual_account": balance_service.get_virtual_account_balance()
    })

@router.get("/accounts")
def get_account_balances(balance_service: BalanceServiceDep):
    return balance_service.get_account_balances(g.user)

@router.get("/fees")
def get_fee_summary(balance_service: BalanceServiceDep):
    return {
        "fees_and_risk_eur": balance_service.get_fees_and_risk_eur()
    }
