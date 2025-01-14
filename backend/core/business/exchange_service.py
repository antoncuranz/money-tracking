from datetime import date
from decimal import Decimal
from typing import Annotated

from fastapi import Depends, HTTPException
from peewee import fn
from pydantic import BaseModel

from backend.core.business.balance_service import BalanceServiceDep
from backend.models import Exchange, ExchangePayment, Payment


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
    def __init__(self, balance_service: BalanceServiceDep):
        self.balance_service = balance_service

    def get_exchanges(self, usable=None):
        query = True
        if usable is True:
            query = query & (Exchange.amount_usd > fn.COALESCE(
                ExchangePayment.select(fn.SUM(ExchangePayment.amount)).join(Payment)
                .where((ExchangePayment.exchange == Exchange.id) & (Payment.status == Payment.Status.PROCESSED.value)), 0
            ))

        return Exchange.select().where(query).order_by(-Exchange.date)
    
    def create_exchange(self, exchange: CreateExchange):
        if exchange.paid_eur == 0:  # neutral Exchange => won't affect avg. exchange rate of Payment
            return Exchange.create(
                date=exchange.date, amount_usd=exchange.amount_usd, exchange_rate=Decimal(0), amount_eur=0,
                paid_eur=0, fees_eur=0
            )

        exchange_rate = Decimal(exchange.exchange_rate) / 10000000
        amount_eur = round(Decimal(exchange.amount_usd) / exchange_rate)
        fees_eur = exchange.paid_eur - amount_eur

        return Exchange.create(
            date=exchange.date, amount_usd=exchange.amount_usd, exchange_rate=exchange_rate, amount_eur=amount_eur,
            paid_eur=exchange.paid_eur, fees_eur=fees_eur
        )
    
    def delete_exchange(self, exchange_id):
        exchange = Exchange.get(Exchange.id == exchange_id)

        if not ExchangePayment.select().where(ExchangePayment.exchange == exchange_id):
            exchange.delete_instance()
        else:
            raise HTTPException(status_code=500, detail="Exchange is still in use")
    
    def update_exchange(self, exchange_id, amount, payment_id):
        payment = Payment.get(
            (Payment.id == payment_id) &
            (Payment.status != Payment.Status.PROCESSED.value)
        )
        exchange = Exchange.get(Exchange.id == exchange_id)

        if amount == 0:
            ExchangePayment.delete().where(
                (ExchangePayment.exchange == exchange_id) &
                (ExchangePayment.payment == payment_id)
            ).execute()
            return

        ep = ExchangePayment.get_or_none(exchange=exchange, payment=payment)
        current_amount = 0 if not ep else ep.amount

        if self.balance_service.calc_exchange_remaining(exchange) + current_amount < amount:
            raise HTTPException(status_code=500, detail=f"Error: Exchange {exchange_id} has not enough balance!")

        if self.balance_service.calc_payment_remaining(payment) + current_amount < amount:
            raise HTTPException(status_code=500, detail=f"Error: Exchange {exchange_id} has not enough balance!")

        model, created = ExchangePayment.get_or_create(
            exchange_id=exchange_id,
            payment_id=payment_id,
            defaults={"amount": amount}
        )

        if not created:
            model.amount = amount
            model.save()

ExchangeServiceDep = Annotated[ExchangeService, Depends()]