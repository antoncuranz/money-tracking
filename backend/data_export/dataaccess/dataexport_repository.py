from typing import Optional, List

from sqlmodel import Session, select, true

from models import Account, Transaction, Payment, User


class DataExportRepository:
    def get_unexported_transactions(self, session: Session, account_id: int) -> List[Transaction]:
        stmt = select(Transaction).where(
            (Transaction.status != Transaction.Status.PENDING.value) &
            (Transaction.actual_id.is_(None)) &
            (Transaction.account_id == account_id)
        )
        return session.exec(stmt).all()

    def get_updatable_transactions(self, session: Session, account_id: int) -> List[Transaction]:
        stmt = select(Transaction).where(
            (Transaction.status == Transaction.Status.POSTED.value) &
            (Transaction.actual_id.is_not(None)) &
            (Transaction.amount_eur.is_not(None)) &
            (Transaction.account_id == account_id)
        )
        return session.exec(stmt).all()

    def get_unexported_payments(self, session: Session, account_id: int) -> List[Payment]:
        stmt = select(Payment).where(
            (Payment.actual_id.is_(None)) &
            (Payment.amount_eur.is_not(None)) &
            (Payment.status == Payment.Status.PROCESSED.value) &
            (Payment.account_id == account_id)
        )
        return session.exec(stmt).all()

    def get_account(self, session: Session, user: User, account_id: int) -> Optional[Account]:
        query = (Account.user_id == user.id) if not user.super_user else true()
        stmt = select(Account).where(query & (Account.id == account_id))
        return session.exec(stmt).first()
    
    def get_paid_transactions_by_payment(self, session: Session, payment_id: int) -> List[Transaction]:
        stmt = select(Transaction).join(Account).where(
            (Transaction.payment_id == payment_id) &
            (Transaction.status == Transaction.Status.PAID.value)
        )
        return session.exec(stmt).all()
