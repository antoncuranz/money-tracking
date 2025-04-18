from decimal import Decimal
from typing import Annotated, List

from fastapi import Depends, HTTPException
from sqlmodel import Session

from core.dataaccess.store import Store
from data_export.facade import DataExportFacade
from exchangerate.facade import ExchangeRateFacade
from models import Transaction, User, TransactionWithGuessedAmount


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
            guessed_amount_eur = self.exchangerate.guess_amount_eur(session, transaction)
            exchange_rate = transaction.amount_eur or guessed_amount_eur
            if exchange_rate is not None:
                exchange_rate = (transaction.amount_usd / Decimal(exchange_rate)).quantize(Decimal("0.00000001"))

            return TransactionWithGuessedAmount.model_validate(transaction, update={
                "guessed_amount_eur": guessed_amount_eur,
                "exchange_rate": exchange_rate
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
