from backend.models import Account, Transaction
from backend.data_export.actual_service import ActualService
from flask_injector import inject


class TransactionService:

    @inject
    def __init__(self, actual_service: ActualService):
        self.actual_service = actual_service

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
            self.actual_service.update_transaction(account, transaction)
