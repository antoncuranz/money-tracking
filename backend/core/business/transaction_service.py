from typing import Annotated, List

from fastapi import Depends, HTTPException

from backend.core.dataaccess.store import Store
from backend.data_export.facade import DataExportFacade
from backend.models import Transaction, User


class TransactionService:
    def __init__(self, store: Annotated[Store, Depends()],
                 data_export: Annotated[DataExportFacade, Depends()]):
        self.store = store
        self.data_export = data_export

    def get_transactions(self, user: User, account_id: int = None, paid: bool | None = None) -> List[Transaction]:
        return self.store.get_transactions(user, account_id, paid)

    def update_transaction(self, user: User, tx_id: int, amount_eur):
        transaction = self.store.get_transaction(user, tx_id)
        if not transaction:
            raise HTTPException(status_code=404)
        
        transaction.amount_eur = amount_eur
        self.store.save(transaction)

        if transaction.actual_id is not None:
            self.data_export.update_transaction(user, transaction.account.id, transaction)
