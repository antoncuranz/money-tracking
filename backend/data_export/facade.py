from typing import List, Annotated

from fastapi import Depends

from backend.data_export.business.actual_service import ActualService
from backend.models import Transaction, Payment, User


class DataExportFacade:
    def __init__(self, actual_service: Annotated[ActualService, Depends()]):
        self.actual_service = actual_service

    def export_transactions(self, user: User, account_id: int):
        self.actual_service.export_transactions(user, account_id)

    def update_transactions(self, user: User, account_id: int, transactions: List[Transaction] | None = None):
        self.actual_service.update_transactions(user, account_id, transactions)

    def update_transaction(self, user: User, account_id: int, transaction: Transaction):
        self.actual_service.update_transaction(user, account_id, transaction)

    def export_payments(self, user: User, account_id: int):
        self.actual_service.export_payments(user, account_id)

    def export_payment(self, user: User, account_id: int, payment: Payment):
        self.actual_service.export_payment(user, account_id, payment)

    def delete_transaction(self, user: User, actual_id: int):
        self.actual_service.delete_transaction(user, actual_id)
