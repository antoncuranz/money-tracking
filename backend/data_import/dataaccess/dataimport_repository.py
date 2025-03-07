import datetime
from typing import Optional, List

from peewee import fn

from backend.models import Account, Transaction, Credit, Payment
from backend.models import User, BankAccount


class DataImportRepository:
    
    def get_account(self, user: User, account_id: int) -> Optional[Account]:
        return Account.get_or_none((Account.user == user.id) & (Account.id == account_id))
    
    def get_all_accounts(self) -> List[Account]:
        return Account.select()
    
    def get_all_bank_accounts(self) -> List[BankAccount]:
        return BankAccount.select()
    
    def get_pending_payment(self, account_id: int, due_date: datetime.date, amount_usd: int | None = None) -> Optional[Payment]:
        query = (Payment.account == account_id) & (Payment.date == due_date) & (Payment.status == Payment.Status.PENDING.value)
        
        if amount_usd is not None:
            query = query & (Payment.amount_usd == amount_usd)
            
        return Payment.get_or_none(query)
    
    def create_pending_payment(self, account: Account, statement_date: datetime.date, last_statement_date: datetime.date, due_date: datetime.date) -> Payment:
        amount_usd = Transaction.select(fn.SUM(Transaction.amount_usd)).where(
            (Transaction.account == account.id) & (Transaction.status == Transaction.Status.POSTED.value) & (Transaction.date <= statement_date)
        ).scalar() or 0
        amount_usd -= Credit.select(fn.SUM(Credit.amount_usd)).where(
            (Credit.account == account.id) & (Credit.date <= statement_date) & (Credit.date > last_statement_date)
        ).scalar() or 0
        # TODO: subtract unprocessed payments
        return Payment.create(account_id=account.id, date=due_date, counterparty=account.institution, description="Upcoming Payment", amount_usd=amount_usd, status_enum=Payment.Status.PENDING)

    def get_pending_payments_between(self, bank_account_id: int, date_from: datetime.date, date_to: datetime.date) -> List[Payment]:
        return Payment.select().join(Account).where(
            (Account.bank_account == bank_account_id) & (Payment.status == Payment.Status.PENDING.value) & (date_from <= Payment.date <= date_to)
        )
    
    def get_or_create_payment(self, import_id: str, args) -> tuple[Payment, bool]:
        result, created = Payment.get_or_create(
            import_id=import_id,
            defaults=args
        )
        return result, created

    def get_or_create_transaction(self, import_id: str, args) -> tuple[Transaction, bool]:
        result, created = Transaction.get_or_create(
            import_id=import_id,
            defaults=args
        )
        return result, created
    
    def get_or_create_credit(self, import_id: str, args) -> tuple[Credit, bool]:
        result, created = Credit.get_or_create(
            import_id=import_id,
            defaults=args
        )
        return result, created
    
    def update_payment(self, payment_id: int, args):
        Payment.update(**args).where(Payment.id == payment_id).execute()
