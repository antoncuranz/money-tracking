import datetime
from decimal import Decimal
from typing import Optional, List

from sqlmodel import Session, select

from backend.models import ExchangeRate, Transaction


class ExchangeRateRepository:
    def get_exchange_rate(self, session: Session, date: datetime.date, source: ExchangeRate.Source) -> Optional[ExchangeRate]:
        stmt = select(ExchangeRate).where((ExchangeRate.date == date) & (ExchangeRate.source == source.value))
        return session.exec(stmt).first()
    
    def persist_exchange_rate(self, session: Session, date: datetime.date, source: ExchangeRate.Source, rate: Decimal) -> ExchangeRate:
        exchange_rate = ExchangeRate(date=date, source=source, exchange_rate=rate)
        session.add(exchange_rate)
        return exchange_rate

    def get_transactions_without_eur_amount(self, session: Session, account_id: int) -> List[Transaction]:
        stmt = select(Transaction).where((Transaction.account_id == account_id) & (Transaction.amount_eur.is_(None)))
        return session.exec(stmt).all()