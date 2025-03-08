from typing import List, Optional

from sqlmodel import Session, select, func

from models import Transaction, User, Account


class TransactionRepository:
    def get_transaction(self, session: Session, user: User, tx_id: int) -> Optional[Transaction]:
        stmt = select(Transaction).where(Transaction.id == tx_id)
        return session.exec(stmt).first()  # TODO: check user!

    def get_transactions(self, session: Session, user: User, account_id: int = None, paid: bool | None = None) -> List[Transaction]:
        query = (Account.user_id == user.id)

        if paid is True:
            query = query & (Transaction.status == Transaction.Status.PAID.value)
        elif paid is False:
            query = query & (Transaction.status != Transaction.Status.PAID.value)

        if account_id is not None:
            query = query & (Transaction.account_id == account_id)

        stmt = select(Transaction).join(Account).where(query).order_by(Transaction.date.desc(), Transaction.id.desc())
        return session.exec(stmt).all()

    def get_paid_transactions_by_payment(self, session: Session, user: User, payment_id: int) -> List[Transaction]:
        stmt = select(Transaction).join(Account).where(
            (Account.user_id == user.id) &
            (Transaction.payment_id == payment_id) &
            (Transaction.status == Transaction.Status.PAID.value)
        )
        return session.exec(stmt).all()

    def get_posted_transactions_by_account(self, session: Session, account_id: int) -> List[Transaction]:
        stmt = select(Transaction).where(
            (Transaction.status == Transaction.Status.POSTED.value) &
            (Transaction.account_id == account_id)
        ).order_by(Transaction.date, Transaction.id)
        return session.exec(stmt).all()

    def get_posted_transaction_amount(self, session: Session, account_id: int) -> int:
        stmt = select(func.sum(Transaction.amount_usd)).where(
            (Transaction.account_id == account_id) & (Transaction.status != Transaction.Status.PENDING.value)
        )
        return session.exec(stmt).first() or 0

    def get_pending_transaction_amount(self, session: Session, account_id: int) -> int:
        stmt = select(func.sum(Transaction.amount_usd)).where(
            (Transaction.account_id == account_id) & (Transaction.status == Transaction.Status.PENDING.value) &
            Transaction.ignore.is_not(True)
        )
        return session.exec(stmt).first() or 0

    def get_all_posted_transactions(self, session: Session) -> List[Transaction]:
        stmt = select(Transaction).where(Transaction.status == Transaction.Status.POSTED.value)
        return session.exec(stmt).all()

    def get_balance_pending(self, session: Session) -> int:
        stmt = select(func.sum(Transaction.amount_usd)).where(
            (Transaction.status == Transaction.Status.PENDING.value) & Transaction.ignore.is_not(True)
        )
        return session.exec(stmt).first() or 0

    def get_fees_and_risk_eur(self, session: Session) -> int:
        stmt = select(func.sum(Transaction.fees_and_risk_eur))\
            .where(Transaction.status == Transaction.Status.PAID.value)
        return session.exec(stmt).first() or 0
