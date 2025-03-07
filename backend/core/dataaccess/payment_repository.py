from typing import List, Optional

from peewee import fn

from backend.models import User, Account, Payment


class PaymentRepository:
    def get_payment(self, user: User, payment_id: int) -> Optional[Payment]:
        return Payment.get_or_none(Payment.id == payment_id)  # TODO: check user!

    def get_payments(self, user: User, account_id: int, processed: bool | None = None):
        query = (Account.user == user.id)

        if processed is not None:
            query = query & (
                Payment.status == Payment.Status.PROCESSED.value if processed else Payment.status != Payment.Status.PROCESSED.value)

        if account_id is not None:
            query = query & (Payment.account == account_id)

        return Payment.select().join(Account).where(query).order_by(-Payment.date)

    def get_unprocessed_payment(self, payment_id: int) -> Optional[Payment]:
        return Payment.get_or_none(
            (Payment.id == payment_id) &
            (Payment.status != Payment.Status.PROCESSED.value)
        )

    def get_posted_payment_amount(self, account_id: int) -> int:
        return Payment.select(fn.SUM(Payment.amount_usd)).where(
            (Payment.account == account_id) & (Payment.status != Payment.Status.PENDING.value)
        ).scalar() or 0

    def get_all_posted_payments(self) -> List[Payment]:
        return Payment.select().where(Payment.status == Payment.Status.POSTED.value)
