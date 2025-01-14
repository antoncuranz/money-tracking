from typing import Annotated

from fastapi import Depends
from peewee import DoesNotExist

from backend.exchangerate.adapter.exchangerates_client import IExchangeRateClient, ExchangeratesApiIoClient, \
    MastercardClient
from backend.models import Transaction, ExchangeRate


class ExchangeRateService:
    def __init__(self, mastercard: Annotated[IExchangeRateClient, Depends(MastercardClient)],
                 exchangeratesio: Annotated[IExchangeRateClient, Depends(ExchangeratesApiIoClient)]):
        self.mastercard = mastercard
        self.exchangeratesio = exchangeratesio
        
    def fetch_exchange_rates(self, account, source: ExchangeRate.Source = ExchangeRate.Source.MASTERCARD):
        transactions = Transaction.select().where((Transaction.account == account.id) & (Transaction.amount_eur.is_null()))
        [self._get_exchange_rate(date, source) for date in set([tx.date for tx in transactions])]

    def guess_amount_eur(self, transaction: Transaction):
        try:
            exchange_rate = self._get_exchange_rate(transaction.date)
            return int(transaction.amount_usd / exchange_rate)
        except:
            return None

    def _get_exchange_rate(self, date, source: ExchangeRate.Source = ExchangeRate.Source.MASTERCARD):
        try:
            return ExchangeRate.get(date=date, source=source.value).exchange_rate
        except DoesNotExist:
            if source == ExchangeRate.Source.MASTERCARD:
                return self.mastercard.get_conversion_rate(date)
            elif source == ExchangeRate.Source.EXCHANGERATESIO:
                return self.exchangeratesio.get_conversion_rate(date)
            else:
                raise Exception("Not implemented")

ExchangeRateServiceDep = Annotated[ExchangeRateService, Depends()]