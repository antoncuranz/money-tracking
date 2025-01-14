from typing import Annotated
from fastapi import Depends, HTTPException
from backend.core.service.balance_service import BalanceServiceDep
from backend.models import Account, Credit, CreditTransaction, Transaction
from peewee import fn


class CreditService:
    def __init__(self, balance_service: BalanceServiceDep):
        self.balance_service = balance_service

    def get_credits(self, user, account_id, usable=None):
        query = (Account.user == user.id)
        
        if usable is True:
            query = query & (Credit.amount_usd > fn.COALESCE(
                CreditTransaction.select(fn.SUM(CreditTransaction.amount)).join(Transaction)
                .where((CreditTransaction.credit == Credit.id) & (Transaction.status == Transaction.Status.PAID.value)),
                0
            ))

        if account_id is not None:
            query = query & (Credit.account == account_id)

        return Credit.select().join(Account).where(query).order_by(-Credit.date)

    def update_credit(self, user, credit_id, transaction_id, amount):
        tx = Transaction.get(
            (Transaction.id == transaction_id) &
            (Transaction.status != Transaction.Status.PAID.value)
        )
        credit = Credit.get((Credit.id == credit_id) & (Credit.account == tx.account_id))
        Account.get((Account.user == user.id) & (Account.id == credit.account))

        if amount == 0:
            CreditTransaction.delete().where(
                (CreditTransaction.credit == credit_id) &
                (CreditTransaction.transaction == transaction_id)
            ).execute()
            return

        ct = CreditTransaction.get_or_none(credit=credit, transaction=tx)
        current_amount = 0 if not ct else ct.amount

        if self.balance_service.calc_credit_remaining(credit) + current_amount < amount:
            raise HTTPException(status_code=500, detail=f"Error: Credit {credit_id} has not enough balance!")

        if self.balance_service.calc_transaction_remaining(tx) + current_amount < amount:
            raise HTTPException(status_code=500, detail=f"Error: Transaction {transaction_id} has not enough balance!")

        model, created = CreditTransaction.get_or_create(
            credit_id=credit_id,
            transaction_id=transaction_id,
            defaults={"amount": amount}
        )

        if not created:
            model.amount = amount
            model.save()

CreditServiceDep = Annotated[CreditService, Depends()]