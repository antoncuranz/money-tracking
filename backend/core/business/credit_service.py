from typing import Annotated
from fastapi import Depends, HTTPException
from sqlmodel import Session
from backend.core.business.balance_service import BalanceService
from backend.core.dataaccess.store import Store
from backend.models import Transaction, User, engine


class CreditService:
    def __init__(self, store: Annotated[Store, Depends()], balance_service: Annotated[BalanceService, Depends()]):
        self.store = store
        self.balance_service = balance_service

    def get_credits(self, session: Session, user: User, account_id: int, usable: bool | None = None):
        return self.store.get_credits(session, user, account_id, usable)

    def update_credit(self, session: Session, user: User, credit_id: int, transaction_id: int, amount: int):
        tx = self.store.get_transaction(session, user, transaction_id)
        credit = self.store.get_credit(session, tx.account_id, credit_id)
        if not tx or not credit:
            raise HTTPException(status_code=404)
        if tx.status == Transaction.Status.PAID.value:
            raise HTTPException(status_code=400, detail="Transaction already paid")

        if amount == 0:
            self.store.delete_credit_transaction(session, credit_id, transaction_id)
            return

        ct = self.store.get_credit_transaction(session, credit_id, transaction_id)
        current_amount = 0 if not ct else ct.amount

        if self.balance_service.calc_credit_remaining(session, credit) + current_amount < amount:
            raise HTTPException(status_code=400, detail=f"Error: Credit {credit_id} has not enough balance!")

        if self.balance_service.calc_transaction_remaining(session, tx) + current_amount < amount:
            raise HTTPException(status_code=400, detail=f"Error: Transaction {transaction_id} has not enough balance!")

        model, created = self.store.get_or_create_credit_transaction(session, credit_id, transaction_id, amount)

        if not created:
            model.amount = amount
            session.add(model)
        session.commit()
