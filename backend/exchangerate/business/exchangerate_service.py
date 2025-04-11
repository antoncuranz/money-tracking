import datetime
from decimal import Decimal
from typing import Annotated, Optional

from fastapi import Depends
from sqlmodel import Session

from exchangerate.adapter.exchangerates_client import IExchangeRateClient, ExchangeratesApiIoClient, \
    MastercardClient
from exchangerate.dataaccess.exchangerate_repository import ExchangeRateRepository
from models import Transaction, ExchangeRate, Account


class ExchangeRateService:
    def __init__(self, mastercard: Annotated[IExchangeRateClient, Depends(MastercardClient)],
                 exchangeratesio: Annotated[IExchangeRateClient, Depends(ExchangeratesApiIoClient)],
                 repository: Annotated[ExchangeRateRepository, Depends()]):
        self.mastercard = mastercard
        self.exchangeratesio = exchangeratesio
        self.repository = repository
        
    def fetch_exchange_rates(self, session: Session, account: Account, source: ExchangeRate.Source = ExchangeRate.Source.MASTERCARD):
        transactions = self.repository.get_transactions_without_eur_amount(session, account.id)
        [self.get_exchange_rate(session, date, source) for date in set([tx.date for tx in transactions])]

    def guess_amount_eur(self, session: Session, transaction: Transaction) -> int | None:
        try:
            exchange_rate = self.get_exchange_rate(session, transaction.date)
            return int(transaction.amount_usd / exchange_rate)
        except:
            return None

    def get_exchange_rate(self, session: Session, date: datetime.date, source: ExchangeRate.Source = ExchangeRate.Source.MASTERCARD) -> Optional[Decimal]:
        er = self.repository.get_exchange_rate(session, date, source)
        if not er:
            if source == ExchangeRate.Source.MASTERCARD:
                rate = self.mastercard.get_conversion_rate(date)
            elif source == ExchangeRate.Source.EXCHANGERATESIO:
                rate = self.exchangeratesio.get_conversion_rate(date)
            else:
                raise Exception("Not implemented")
            
            if rate:
                self.repository.persist_exchange_rate(session, date, source.value, rate)
                session.commit()
            return rate
        else:
            return er.exchange_rate
