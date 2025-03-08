import datetime
from decimal import Decimal
from typing import List, Optional

from sqlmodel import Session, select, func

from models import Payment, ExchangePayment, Exchange


class ExchangeRepository:
    def get_exchanges(self, session: Session, usable=None) -> List[Exchange]:
        query = True
        if usable is True:
            amount_used = (
                select(func.sum(ExchangePayment.amount)).join(Payment)
                .where(
                    (ExchangePayment.exchange_id == Exchange.id) & (Payment.status == Payment.Status.PROCESSED.value)
                ).scalar_subquery()
            )
            query = Exchange.amount_usd > func.coalesce(amount_used, 0)

        stmt = select(Exchange).where(query).order_by(Exchange.date.desc())
        return session.exec(stmt).all()

    def get_exchange(self, session: Session, exchange_id: int) -> Optional[Exchange]:
        stmt = select(Exchange).where(Exchange.id == exchange_id)
        return session.exec(stmt).first()

    def create_exchange(self, session: Session, date: datetime.date, amount_usd: int, exchange_rate: Decimal,
                        amount_eur: int, paid_eur: int, fees_eur: int) -> Exchange:
        exchange = Exchange(
            date=date, amount_usd=amount_usd, exchange_rate=exchange_rate, amount_eur=amount_eur,
            paid_eur=paid_eur, fees_eur=fees_eur
        )
        session.add(exchange)
        return exchange

    #### EXCHANGE PAYMENTS ####
    
    def get_exchange_payment(self, session: Session, exchange_id: int, payment_id: int) -> Optional[ExchangePayment]:
        stmt = select(ExchangePayment).where(
            (ExchangePayment.exchange_id == exchange_id) & (ExchangePayment.payment_id == payment_id)
        )
        return session.exec(stmt).first()

    def get_exchange_payments_by_exchange(self, session: Session, exchange_id: int) -> List[ExchangePayment]:
        stmt = select(ExchangePayment).where(ExchangePayment.exchange_id == exchange_id)
        return session.exec(stmt).all()

    def get_exchange_payments_by_payment(self, session: Session, payment_id: int) -> List[ExchangePayment]:
        stmt = select(ExchangePayment).where(ExchangePayment.payment_id == payment_id)
        return session.exec(stmt).all()

    def get_exchange_payment_amount(self, session: Session, exchange_id: int, payment_id: int) -> int:
        ep = self.get_exchange_payment(session, exchange_id, payment_id)
        return 0 if not ep else ep.amount

    def delete_exchange_payment(self, session: Session, exchange_id: int, payment_id: int):
        ep = self.get_exchange_payment(session, exchange_id, payment_id)
        if not ep:
            raise RuntimeError(f"Exchange payment not found!")
        session.delete(ep)

    def get_or_create_exchange_payment(self, session: Session, exchange_id: int, payment_id: int, amount: int)\
            -> tuple[ExchangePayment, bool]:
        model = self.get_exchange_payment(session, exchange_id, payment_id)
        created = not model
        
        if created:
            model = ExchangePayment(exchange_id=exchange_id, payment_id=payment_id, amount=amount)
        session.add(model)
        
        return model, created
