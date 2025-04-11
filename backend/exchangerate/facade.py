import datetime
from decimal import Decimal
from typing import Annotated

from exchangerate.business.exchangerate_service import ExchangeRateService
from fastapi import Depends
from models import Account, Transaction
from sqlmodel import Session


class ExchangeRateFacade:
    def __init__(self, exchangerate_service: Annotated[ExchangeRateService, Depends()]):
        self.exchangerate_service = exchangerate_service

    def fetch_exchange_rates(self, session: Session, account: Account):
        self.exchangerate_service.fetch_exchange_rates(session, account)

    def guess_amount_eur(self, session: Session, transaction: Transaction) -> int | None:
        return self.exchangerate_service.guess_amount_eur(session, transaction)

    def get_exchange_rate(self, session: Session, date: datetime.date) -> Decimal:
        return self.exchangerate_service.get_exchange_rate(session, date)

