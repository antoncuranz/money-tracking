from typing import List
from sqlmodel import Session, select

from models import Account, User


class DatesRepository:
    def get_all_accounts(self, session: Session) -> List[Account]:
        stmt = select(Account).order_by(Account.id)
        return session.exec(stmt).all()
    
    def get_accounts_of_user(self, session: Session, user: User) -> List[Account]:
        stmt = select(Account).where(Account.user_id == user.id).order_by(Account.id)
        return session.exec(stmt).all()
