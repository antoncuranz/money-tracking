import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Depends

from backend.exchangerate.adapter.exchangerates_client import IExchangeRateClient, ExchangeratesApiIoClient, \
    MastercardClient
from backend.exchangerate.dataaccess.exchangerate_repository import ExchangeRateRepository
from backend.models import Transaction, ExchangeRate, Account


class ExchangeRateService:
    def __init__(self, mastercard: Annotated[IExchangeRateClient, Depends(MastercardClient)],
                 exchangeratesio: Annotated[IExchangeRateClient, Depends(ExchangeratesApiIoClient)],
                 repository: Annotated[ExchangeRateRepository, Depends()]):
        self.mastercard = mastercard
        self.exchangeratesio = exchangeratesio
        self.repository = repository
        
    def fetch_exchange_rates(self, account: Account, source: ExchangeRate.Source = ExchangeRate.Source.MASTERCARD):
        transactions = self.repository.get_transactions_without_eur_amount(account.id)
        [self._get_exchange_rate(date, source) for date in set([tx.date for tx in transactions])]

    def guess_amount_eur(self, transaction: Transaction) -> int | None:
        try:
            exchange_rate = self._get_exchange_rate(transaction.date)
            return int(transaction.amount_usd / exchange_rate)
        except:
            return None

    def _get_exchange_rate(self, date: datetime.date, source: ExchangeRate.Source = ExchangeRate.Source.MASTERCARD) -> Decimal:
        er = self.repository.get_exchange_rate(date, source)
        if not er:
            if source == ExchangeRate.Source.MASTERCARD:
                rate = self.mastercard.get_conversion_rate(date)
            elif source == ExchangeRate.Source.EXCHANGERATESIO:
                rate = self.exchangeratesio.get_conversion_rate(date)
            else:
                raise Exception("Not implemented")
            
            return self.repository.persist_exchange_rate(date, source.value, rate).exchange_rate
        else:
            return er.exchange_rate
