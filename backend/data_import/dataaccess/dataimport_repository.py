import datetime
from typing import Optional, List

from sqlmodel import Session, select, func

from backend.models import Account, Transaction, Credit, Payment
from backend.models import User, BankAccount


class DataImportRepository:
    
    def get_account(self, session: Session, user: User, account_id: int) -> Optional[Account]:
        stmt = select(Account).where((Account.user_id == user.id) & (Account.id == account_id))
        return session.exec(stmt).first()
    
    def get_all_accounts(self, session: Session) -> List[Account]:
        return session.exec(select(Account)).all()
    
    def get_all_bank_accounts(self, session: Session) -> List[BankAccount]:
        return session.exec(select(BankAccount)).all()

    def get_pending_payment(self, session: Session, account_id: int, due_date: datetime.date, amount_usd: int | None = None) -> Optional[Payment]:
        query = (Payment.account_id == account_id) & (Payment.date == due_date) & (Payment.status == Payment.Status.PENDING.value)
        
        if amount_usd is not None:
            query = query & (Payment.amount_usd == amount_usd)
        
        stmt = select(Payment).where(query)
        return session.exec(stmt).first()
    
    def create_pending_payment(self, session: Session, account: Account, statement_date: datetime.date, last_statement_date: datetime.date, due_date: datetime.date) -> Payment:
        tx_sum = select(func.sum(Transaction.amount_usd)).where(
            (Transaction.account_id == account.id) & (Transaction.status == Transaction.Status.POSTED.value) & (Transaction.date <= statement_date) & (Transaction.date > last_statement_date)
        )
        credit_sum = select(func.sum(Credit.amount_usd)).where(
            (Credit.account_id == account.id) & (Credit.date <= statement_date) & (Credit.date > last_statement_date)
        )
        amount_usd = (session.exec(tx_sum).first() or 0) - (session.exec(credit_sum).first() or 0)
        
        payment = Payment(account_id=account.id, date=due_date, counterparty=account.institution, description="Upcoming Payment", amount_usd=amount_usd, status=Payment.Status.PENDING.value)
        session.add(payment)
        return payment

    def get_pending_payments_between(self, session: Session, bank_account_id: int, date_from: datetime.date, date_to: datetime.date) -> List[Payment]:
        stmt = select(Payment).join(Account).where(
            (Account.bank_account_id == bank_account_id) & (Payment.status == Payment.Status.PENDING.value) & (date_from <= Payment.date) & (Payment.date <= date_to)
        )
        return session.exec(stmt).all()
    
    def get_payment_by_import_id(self, session: Session, import_id: str) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.import_id == import_id)
        return session.exec(stmt).first()
    
    def get_credit_by_import_id(self, session: Session, import_id: str) -> Optional[Credit]:
        stmt = select(Credit).where(Credit.import_id == import_id)
        return session.exec(stmt).first()
    
    def get_transaction_by_import_id(self, session: Session, import_id: str) -> Optional[Transaction]:
        stmt = select(Transaction).where(Transaction.import_id == import_id)
        return session.exec(stmt).first()

    def get_or_create_payment(self, session: Session, import_id: str, args) -> tuple[Payment, bool]:
        model = self.get_payment_by_import_id(session, import_id)
        created = not model

        if created:
            model = Payment(**args)
        session.add(model)

        return model, created

    def get_or_create_transaction(self, session: Session, import_id: str, args) -> tuple[Transaction, bool]:
        model = self.get_transaction_by_import_id(session, import_id)
        created = not model

        if created:
            model = Transaction(**args)
        session.add(model)

        return model, created
    
    def get_or_create_credit(self, session: Session, import_id: str, args) -> tuple[Credit, bool]:
        model = self.get_credit_by_import_id(session, import_id)
        created = not model

        if created:
            model = Credit(**args)
        session.add(model)

        return model, created
