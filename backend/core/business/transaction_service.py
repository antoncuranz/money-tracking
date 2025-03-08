from typing import Annotated, List

from fastapi import Depends, HTTPException
from sqlmodel import Session

from backend.core.dataaccess.store import Store
from backend.data_export.facade import DataExportFacade
from backend.exchangerate.facade import ExchangeRateFacade
from backend.models import Transaction, User, engine, TransactionWithGuessedAmount


class TransactionService:
    def __init__(self, store: Annotated[Store, Depends()],
                 data_export: Annotated[DataExportFacade, Depends()],
                 exchangerate: Annotated[ExchangeRateFacade, Depends()]):
        self.store = store
        self.data_export = data_export
        self.exchangerate = exchangerate

    def get_transactions_with_guessed_amount(self, session: Session, user: User, account_id: int = None, paid: bool | None = None) -> List[TransactionWithGuessedAmount]:
        transactions = self.store.get_transactions(session, user, account_id, paid)

        def map_transaction(transaction: Transaction):
            return TransactionWithGuessedAmount.model_validate(transaction, update={
                "guessed_amount_eur": self.exchangerate.guess_amount_eur(session, transaction)
            })

        return [map_transaction(tx) for tx in transactions]


    def update_transaction(self, session: Session, user: User, tx_id: int, amount_eur):
        transaction = self.store.get_transaction(session, user, tx_id)
        if not transaction:
            raise HTTPException(status_code=404)
        
        transaction.amount_eur = amount_eur
        session.add(transaction)
        session.commit()

        if transaction.actual_id is not None:
            self.data_export.update_transaction(session, user, transaction.account.id, transaction)
