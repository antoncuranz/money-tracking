from typing import Annotated

from fastapi import Depends

from backend.exchangerate.business.exchangerate_service import ExchangeRateService
from backend.models import Account, Transaction


class ExchangeRateFacade:
    def __init__(self, exchangerate_service: Annotated[ExchangeRateService, Depends()]):
        self.exchangerate_service = exchangerate_service

    def fetch_exchange_rates(self, account: Account):
        self.exchangerate_service.fetch_exchange_rates(account)

    def guess_amount_eur(self, transaction: Transaction):
        return self.exchangerate_service.guess_amount_eur(transaction)

