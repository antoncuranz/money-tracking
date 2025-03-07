import datetime
from decimal import Decimal
from typing import List, Optional

from peewee import fn

from backend.models import Payment, ExchangePayment, Exchange


class ExchangeRepository:
    def get_exchanges(self, usable=None) -> List[Exchange]:
        query = True
        if usable is True:
            query = query & (Exchange.amount_usd > fn.COALESCE(
                ExchangePayment.select(fn.SUM(ExchangePayment.amount)).join(Payment)
                .where((ExchangePayment.exchange == Exchange.id) & (Payment.status == Payment.Status.PROCESSED.value)),
                0
            ))

        return Exchange.select().where(query).order_by(-Exchange.date)

    def get_exchange(self, exchange_id: int) -> Optional[Exchange]:
        return Exchange.get_or_none(Exchange.id == exchange_id)

    def create_exchange(self, date: datetime.date, amount_usd: int, exchange_rate: Decimal, amount_eur: int,
                        paid_eur: int, fees_eur: int) -> Exchange:
        return Exchange.create(
            date=date, amount_usd=amount_usd, exchange_rate=exchange_rate, amount_eur=amount_eur,
            paid_eur=paid_eur, fees_eur=fees_eur
        )

    #### EXCHANGE PAYMENTS ####

    def get_exchange_payments_by_exchange(self, exchange_id: int) -> List[ExchangePayment]:
        return ExchangePayment.select().where(ExchangePayment.exchange == exchange_id)

    def get_exchange_payments_by_payment(self, payment_id: int) -> List[ExchangePayment]:
        return ExchangePayment.select().where(ExchangePayment.payment == payment_id)

    def get_exchange_payment_amount(self, exchange_id: int, payment_id: int):
        ep = ExchangePayment.get_or_none(exchange=exchange_id, payment=payment_id)
        return 0 if not ep else ep.amount

    def delete_exchange_payment(self, exchange_id: int, payment_id: int):
        ExchangePayment.delete().where(
            (ExchangePayment.exchange == exchange_id) &
            (ExchangePayment.payment == payment_id)
        ).execute()

    def get_or_create_exchange_payment(self, exchange_id: int, payment_id: int, amount: int) -> tuple[
        ExchangePayment, bool]:
        model, created = ExchangePayment.get_or_create(
            exchange_id=exchange_id,
            payment_id=payment_id,
            defaults={"amount": amount}
        )
        return model, created
