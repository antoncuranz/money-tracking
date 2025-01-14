from typing import Annotated

from fastapi import Depends

from backend.data_export.facade import DataExportDep
from backend.models import Account, Transaction


class TransactionService:
    def __init__(self, data_export: DataExportDep):
        self.data_export = data_export

    def get_transactions(self, user, account_id=None, paid=None):
        query = (Account.user == user.id)

        if paid is True:
            query = query & (Transaction.status == Transaction.Status.PAID.value)
        elif paid is False:
            query = query & (Transaction.status != Transaction.Status.PAID.value)

        if account_id is not None:
            query = query & (Transaction.account == account_id)

        return Transaction.select().join(Account).where(query).order_by(-Transaction.date)
    
    def update_transaction(self, user, tx_id, amount_eur):
        """
        Raises
        ------
        DoesNotExist
            If a transaction with the given `tx_id` does not exist or does not belong to the given `user`.
        """
        transaction = Transaction.get(Transaction.id == tx_id)
        account = Account.get((Account.user == user.id) & (Account.id == transaction.account))
        
        transaction.amount_eur = amount_eur
        transaction.save()

        if transaction.actual_id is not None:
            self.data_export.update_transaction(account, transaction)

TransactionServiceDep = Annotated[TransactionService, Depends()]
