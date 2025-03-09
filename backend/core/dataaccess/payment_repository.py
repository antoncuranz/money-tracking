from typing import List, Optional

from sqlmodel import Session, select, func, true

from models import User, Account, Payment


class PaymentRepository:
    def get_payment(self, session: Session, user: User, payment_id: int) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.id == payment_id)
        return session.exec(stmt).first()  # TODO: check user!

    def get_payments(self, session: Session, user: User, account_id: int, processed: bool | None = None):
        query = (Account.user_id == user.id) if not user.super_user else true()

        if processed is not None:
            query = query & (
                Payment.status == Payment.Status.PROCESSED.value if processed else Payment.status != Payment.Status.PROCESSED.value)

        if account_id is not None:
            query = query & (Payment.account_id == account_id)

        stmt = select(Payment).join(Account).where(query).order_by(Payment.date.desc())
        return session.exec(stmt).all()

    def get_unprocessed_payment(self, session: Session, payment_id: int) -> Optional[Payment]:
        stmt = select(Payment).where(
            (Payment.id == payment_id) &
            (Payment.status != Payment.Status.PROCESSED.value)
        )
        return session.exec(stmt).first()

    def get_posted_payment_amount(self, session: Session, account_id: int) -> int:
        stmt = select(func.sum(Payment.amount_usd)).where(
            (Payment.account_id == account_id) & (Payment.status != Payment.Status.PENDING.value)
        )
        return session.exec(stmt).first() or 0

    def get_all_posted_payments(self, session: Session) -> List[Payment]:
        stmt = select(Payment).where(Payment.status == Payment.Status.POSTED.value)
        return session.exec(stmt).all()
