from typing import List, Optional

from sqlmodel import Session, select, func

from models import Transaction, User, Account, CreditTransaction, Credit


class CreditRepository:
    def get_credit(self, session: Session, account_id: int, credit_id: int) -> Optional[Credit]:
        stmt = select(Credit).where((Credit.id == credit_id) & (Credit.account_id == account_id))
        return session.exec(stmt).first()

    def get_credits(self, session: Session, user: User, account_id: int, usable: bool | None = None) -> List[Credit]:
        query = (Account.user_id == user.id)

        if usable is True:
            amount_used = (
                select(func.sum(CreditTransaction.amount)).join(Transaction)
                .where(
                    (CreditTransaction.credit_id == Credit.id) & (Transaction.status == Transaction.Status.PAID.value)
                ).scalar_subquery()
            )
            query = query & (Credit.amount_usd > func.coalesce(amount_used, 0))

        if account_id is not None:
            query = query & (Credit.account_id == account_id)

        stmt = select(Credit).join(Account).where(query).order_by(Credit.date.desc())
        return session.exec(stmt).all()

    def get_all_credits(self, session: Session) -> List[Credit]:
        return session.exec(select(Credit)).all()

    def get_posted_credit_amount(self, session: Session, account_id: int) -> int:
        stmt = select(func.sum(Credit.amount_usd)).where(
            (Credit.account_id == account_id)
        )
        return session.exec(stmt).first() or 0

    #### CREDIT TRANSACTIONS ####

    def get_credit_transaction(self, session: Session, credit_id: int, transaction_id: int) -> Optional[CreditTransaction]:
        stmt = select(CreditTransaction).where(
            (CreditTransaction.credit_id == credit_id) & (CreditTransaction.transaction_id == transaction_id)
        )
        return session.exec(stmt).first()

    def get_credit_transactions_by_credit(self, session: Session, credit_id: int) -> List[CreditTransaction]:
        stmt = select(CreditTransaction).where(CreditTransaction.credit_id == credit_id)
        return session.exec(stmt).all()

    def get_credit_transactions_by_transaction(self, session: Session, transaction_id: int) -> List[CreditTransaction]:
        stmt = select(CreditTransaction).where(CreditTransaction.transaction_id == transaction_id)
        return session.exec(stmt).all()

    def delete_credit_transaction(self, session: Session, credit_id: int, transaction_id: int):
        ct = self.get_credit_transaction(session, credit_id, transaction_id)
        if ct:
            session.delete(ct)

    def get_or_create_credit_transaction(self, session: Session, credit_id: int, transaction_id: int, amount: int)\
            -> tuple[CreditTransaction, bool]:
        model = self.get_credit_transaction(session, credit_id, transaction_id)
        created = not model

        if created:
            model = CreditTransaction(credit_id=credit_id, transaction_id=transaction_id, amount=amount)
        session.add(model)

        return model, created
