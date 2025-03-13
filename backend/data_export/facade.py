from typing import List, Annotated

from fastapi import Depends
from sqlmodel import Session

from data_export.business.actual_service import ActualService
from models import Transaction, Payment, User


class DataExportFacade:
    def __init__(self, actual_service: Annotated[ActualService, Depends()]):
        self.actual_service = actual_service

    def export_transactions(self, session: Session, user: User, account_id: int):
        self.actual_service.export_transactions(session, user, account_id)

    def update_transactions(self, session: Session, user: User, account_id: int, transactions: List[Transaction] | None = None):
        self.actual_service.update_transactions(session, user, account_id, transactions)

    def update_transaction(self, session: Session, user: User, account_id: int, transaction: Transaction):
        self.actual_service.update_transaction(session, user, account_id, transaction)

    def export_payment(self, session: Session, super_user: User, account_id: int, payment: Payment):
        self.actual_service.export_payment(session, super_user, account_id, payment)

    def delete_payment(self, super_user: User, actual_id: str):
        self.actual_service.delete_payment(super_user, actual_id)
