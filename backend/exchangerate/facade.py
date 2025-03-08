from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from exchangerate.business.exchangerate_service import ExchangeRateService
from models import Account, Transaction


class ExchangeRateFacade:
    def __init__(self, exchangerate_service: Annotated[ExchangeRateService, Depends()]):
        self.exchangerate_service = exchangerate_service

    def fetch_exchange_rates(self, session: Session, account: Account):
        self.exchangerate_service.fetch_exchange_rates(session, account)

    def guess_amount_eur(self, session: Session, transaction: Transaction):
        return self.exchangerate_service.guess_amount_eur(session, transaction)

