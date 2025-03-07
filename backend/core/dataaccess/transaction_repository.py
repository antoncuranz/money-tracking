from typing import List, Optional

from peewee import fn

from backend.models import Transaction, User, Account


class TransactionRepository:
    def get_transaction(self, user: User, tx_id: int) -> Optional[Transaction]:
        return Transaction.get_or_none(Transaction.id == tx_id)  # TODO: check user!

    def get_transactions(self, user: User, account_id: int = None, paid: bool | None = None) -> List[Transaction]:
        query = (Account.user == user.id)

        if paid is True:
            query = query & (Transaction.status == Transaction.Status.PAID.value)
        elif paid is False:
            query = query & (Transaction.status != Transaction.Status.PAID.value)

        if account_id is not None:
            query = query & (Transaction.account == account_id)

        return Transaction.select().join(Account).where(query).order_by(-Transaction.date)

    def get_paid_transactions_by_payment(self, user: User, payment_id: int):
        return Transaction.select().join(Account).where(
            (Account.user == user.id) &
            (Transaction.payment == payment_id) &
            (Transaction.status == Transaction.Status.PAID.value)
        )

    def get_posted_transactions_by_account(self, account_id: int):
        return Transaction.select().where(
            (Transaction.status == Transaction.Status.POSTED.value) &
            (Transaction.account == account_id)
        ).order_by(Transaction.date)  # TODO: order by date, then id

    def get_posted_transaction_amount(self, account_id: int) -> int:
        return Transaction.select(fn.SUM(Transaction.amount_usd)).where(
            (Transaction.account == account_id) & (Transaction.status != Transaction.Status.PENDING.value)
        ).scalar() or 0

    def get_pending_transaction_amount(self, account_id: int) -> int:
        return Transaction.select(fn.SUM(Transaction.amount_usd)).where(
            (Transaction.account == account_id) & (Transaction.status == Transaction.Status.PENDING.value) &
            (Transaction.ignore.is_null() | ~Transaction.ignore)
        ).scalar() or 0

    def get_all_posted_transactions(self) -> List[Transaction]:
        return Transaction.select().where(Transaction.status == Transaction.Status.POSTED.value)

    def get_balance_pending(self) -> int:
        return Transaction.select(fn.SUM(Transaction.amount_usd)).where(
            (Transaction.status == Transaction.Status.PENDING.value) & (
                        Transaction.ignore.is_null() | ~Transaction.ignore)
        ).scalar() or 0

    def get_fees_and_risk_eur(self) -> int:
        return Transaction.select(fn.SUM(Transaction.fees_and_risk_eur)) \
            .where(Transaction.status == Transaction.Status.PAID.value).scalar()
