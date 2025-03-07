from typing import Optional, List

from backend.models import Account, Transaction, Payment, User


class DataExportRepository:
    def get_unexported_transactions(self, account_id: int) -> List[Transaction]:
        return Transaction.select().where(
            (Transaction.status != Transaction.Status.PENDING.value) &
            (Transaction.actual_id.is_null()) &
            (Transaction.account == account_id))

    def get_updatable_transactions(self, account_id: int) -> List[Transaction]:
        return Transaction.select().where(
            (Transaction.status == Transaction.Status.POSTED.value) &
            (Transaction.actual_id.is_null(False)) &
            (Transaction.amount_eur.is_null(False)) &
            (Transaction.account == account_id))
    
    def get_unexported_payments(self, account_id: int) -> List[Payment]:
        return Payment.select().where(
            (Payment.actual_id.is_null()) &
            (Payment.amount_eur.is_null(False)) &
            (Payment.status == Payment.Status.PROCESSED.value) &
            (Payment.account == account_id))
    
    def get_account(self, user: User, account_id: int) -> Optional[Account]:
        return Account.get_or_none((Account.user == user.id) & (Account.id == account_id))
