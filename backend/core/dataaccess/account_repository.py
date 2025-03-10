from typing import List, Optional

from sqlmodel import Session, select, true

from models import Account, BankAccount, User


class AccountRepository:
    def get_all_accounts(self, session: Session) -> List[Account]:
        stmt = select(Account).order_by(Account.id)
        return session.exec(stmt).all()
    
    def get_accounts_of_user(self, session: Session, user: User) -> List[Account]:
        stmt = select(Account).where(Account.user_id == user.id).order_by(Account.id)
        return session.exec(stmt).all()
    
    def get_account(self, session: Session, user: User, account_id: int) -> Optional[Account]:
        query = (Account.user_id == user.id) if not user.super_user else true()
        
        stmt = select(Account).where(query & (Account.id == account_id))
        return session.exec(stmt).first()

    def create_account(self, session: Session, user: User, bank_account_id: int | None, actual_id: int | None,
                       plaid_account_id: int | None, name: str, institution: str, due_day: int | None,
                       autopay_offset: int | None, icon: str | None, color: str | None,
                       target_spend: int | None) -> Account:
        account = Account(user_id=user.id, bank_account_id=bank_account_id, actual_id=actual_id,
                          plaid_account_id=plaid_account_id, name=name, institution=institution, due_day=due_day,
                          autopay_offset=autopay_offset, icon=icon, color=color, target_spend=target_spend)
        session.add(account)
        return account

    def get_bank_accounts_of_user(self, session: Session, user: User) -> List[BankAccount]:
        stmt = select(BankAccount).where(BankAccount.user_id == user.id).order_by(BankAccount.id)
        return session.exec(stmt).all()
    
    def get_bank_account(self, session: Session, user: User, bank_account_id: int) -> Optional[BankAccount]:
        query = (BankAccount.user_id == user.id) if not user.super_user else true()

        stmt = select(BankAccount).where(query & (BankAccount.id == bank_account_id))
        return session.exec(stmt).first()

    def create_bank_account(self, session: Session, user: User, name: str, institution: str, icon: str | None) -> BankAccount:
        bank_account = BankAccount(user_id=user.id, name=name, institution=institution, icon=icon)
        session.add(bank_account)
        return bank_account
