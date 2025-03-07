import datetime
from decimal import Decimal
from typing import Optional, List

from backend.models import ExchangeRate, Transaction


class ExchangeRateRepository:
    def get_exchange_rate(self, date: datetime.date, source: ExchangeRate.Source) -> Optional[ExchangeRate]:
        return ExchangeRate.get_or_none(date=date, source=source.value)
    
    def persist_exchange_rate(self, date: datetime.date, source: ExchangeRate.Source, rate: Decimal) -> ExchangeRate:
        return ExchangeRate.create(date=date, source=source, exchange_rate=rate)

    def get_transactions_without_eur_amount(self, account_id: int) -> List[Transaction]:
        return Transaction.select().where((Transaction.account == account_id) & (Transaction.amount_eur.is_null()))