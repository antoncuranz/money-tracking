from typing import List, Optional

from peewee import fn

from backend.models import Transaction, User, Account, CreditTransaction, \
    Credit


class CreditRepository:
    def get_credit(self, account_id: int, credit_id: int) -> Optional[Credit]:
        return Credit.get_or_none((Credit.id == credit_id) & (Credit.account == account_id))

    def get_credits(self, user: User, account_id: int, usable: bool | None = None) -> List[Credit]:
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

    def get_all_credits(self) -> List[Credit]:
        return Credit.select()

    def get_posted_credit_amount(self, account_id: int) -> int:
        return Credit.select(fn.SUM(Credit.amount_usd)).where(
            (Credit.account == account_id)
        ).scalar() or 0
    
    #### CREDIT TRANSACTIONS ####

    def get_credit_transaction(self, credit_id: int, transaction_id: int) -> Optional[CreditTransaction]:
        return CreditTransaction.get_or_none(credit=credit_id, transaction=transaction_id)

    def get_credit_transactions_by_credit(self, credit_id: int) -> List[CreditTransaction]:
        return CreditTransaction.select().where(CreditTransaction.credit == credit_id)

    def get_credit_transactions_by_transaction(self, transaction_id: int) -> List[CreditTransaction]:
        return CreditTransaction.select().where(CreditTransaction.transaction == transaction_id)

    def get_or_create_credit_transaction(self, credit_id: int, transaction_id: int, amount: int) -> tuple[
        CreditTransaction, bool]:
        model, created = CreditTransaction.get_or_create(
            credit_id=credit_id,
            transaction_id=transaction_id,
            defaults={"amount": amount}
        )
        return model, created

    def delete_credit_transaction(self, credit_id: int, transaction_id: int):
        CreditTransaction.delete().where(
            (CreditTransaction.credit == credit_id) &
            (CreditTransaction.transaction == transaction_id)
        ).execute()
