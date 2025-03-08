from datetime import date
from decimal import Decimal
from typing import Annotated, List

from fastapi import Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel

from backend.core.business.balance_service import BalanceService
from backend.core.dataaccess.store import Store
from backend.models import Exchange


class CreateExchange(BaseModel):
    actual_id: str | None = None
    date: date
    amount_usd: int
    exchange_rate: int
    amount_eur: int | None = None
    paid_eur: int
    fees_eur: int | None = None
    import_id: str | None = None


class ExchangeService:
    def __init__(self, store: Annotated[Store, Depends()],
                 balance_service: Annotated[BalanceService, Depends()]):
        self.store = store
        self.balance_service = balance_service

    def get_exchanges(self, session: Session, usable: bool | None = None) -> List[Exchange]:
        return self.store.get_exchanges(session, usable)

    def create_exchange(self, session: Session, exchange: CreateExchange) -> Exchange:
        if exchange.paid_eur == 0:  # neutral Exchange => won't affect avg. exchange rate of Payment
            exchange = self.store.create_exchange(
                session, date=exchange.date, amount_usd=exchange.amount_usd, exchange_rate=Decimal(0),
                amount_eur=0, paid_eur=0, fees_eur=0
            )
            session.commit()
            return exchange

        exchange_rate = Decimal(exchange.exchange_rate) / 10000000
        amount_eur = round(Decimal(exchange.amount_usd) / exchange_rate)
        fees_eur = exchange.paid_eur - amount_eur

        exchange = self.store.create_exchange(
            session, date=exchange.date, amount_usd=exchange.amount_usd, exchange_rate=exchange_rate,
            amount_eur=amount_eur, paid_eur=exchange.paid_eur, fees_eur=fees_eur
        )
        session.commit()
        return exchange
    
    def delete_exchange(self, session: Session, exchange_id: int):
        exchange = self.store.get_exchange(session, exchange_id)
        if not exchange:
            raise HTTPException(status_code=404)

        if not self.store.get_exchange_payments_by_exchange(session, exchange_id):
            session.delete(exchange)
            session.commit()
        else:
            raise HTTPException(status_code=500, detail="Exchange is still in use")
    
    def update_exchange(self, session: Session, exchange_id: int, amount: int, payment_id: int):
        payment = self.store.get_unprocessed_payment(session, payment_id)
        exchange = self.store.get_exchange(session, exchange_id)
        if not payment or not exchange:
            raise HTTPException(status_code=404)

        if amount == 0:
            self.store.delete_exchange_payment(session, exchange_id, payment_id)
            session.commit()
            return

        current_amount = self.store.get_exchange_payment_amount(session, exchange_id, payment_id)

        if self.balance_service.calc_exchange_remaining(session, exchange) + current_amount < amount:
            raise HTTPException(status_code=500, detail=f"Error: Exchange {exchange_id} has not enough balance!")

        if self.balance_service.calc_payment_remaining(session, payment) + current_amount < amount:
            raise HTTPException(status_code=500, detail=f"Error: Exchange {exchange_id} has not enough balance!")

        model, created = self.store.get_or_create_exchange_payment(session, exchange_id, payment_id, amount)

        if not created:
            model.amount = amount
            session.add(model)
        session.commit()
