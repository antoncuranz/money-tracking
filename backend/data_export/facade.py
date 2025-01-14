from typing import List, Annotated

from fastapi import Depends

from backend.data_export.business.actual_service import ActualServiceDep
from backend.models import Account, Transaction, Payment, User


class DataExportFacade:
    def __init__(self, actual_service: ActualServiceDep):
        self.actual_service = actual_service

    def export_transactions(self, account: Account):
        self.actual_service.export_transactions(account)

    def export_transaction(self, account: Account, tx: Transaction):
        self.actual_service.xport_transactions(account, tx)

    def update_transactions(self, account: Account, transactions: List[Transaction] | None = None):
        self.actual_service.update_transactions(account, transactions)

    def update_transaction(self, account: Account, transaction: Transaction):
        self.actual_service.update_transaction(account, transaction)

    def export_payments(self, account: Account):
        self.actual_service.export_payments(account)

    def export_payment(self, account: Account, payment: Payment):
        self.actual_service.export_payment(account, payment)

    def delete_transaction(self, user: User, actual_id: int):
        self.actual_service.delete_transaction(user, actual_id)

DataExportDep = Annotated[DataExportFacade, Depends()]
