from flask_injector import inject
from decimal import Decimal

from backend.clients.actual import IActualClient
from backend.models import Transaction, db, Exchange, ExchangePayment, ExchangeRate
from backend.service.balance_service import BalanceService
from backend.service.exchange_service import ExchangeService


class PaymentService:
    @inject
    def __init__(self, balance_service: BalanceService, exchange_service: ExchangeService, actual: IActualClient):
        self.balance_service = balance_service
        self.exchange_service = exchange_service
        self.actual = actual

    def process_payment_auto(self, payment):
        transactions = Transaction.select().where(
            (Transaction.status == Transaction.Status.POSTED.value) &
            (Transaction.account == payment.account)
        ).order_by(Transaction.date)  # TODO: order by date, then id

        self.process_payment(payment, transactions)

    @db.atomic()
    def process_payment(self, payment, transactions):
        if payment.processed or len(payment.transactions) > 0:  # TODO: verify
            raise Exception("Error: Payment was already processed!")

        tx_remaining_sum = sum([self.balance_service.calc_transaction_remaining(tx) for tx in transactions])
        if payment.amount_usd != tx_remaining_sum:
            raise Exception("Error: Payment amount does not match sum of transactions!")

        exchange_payments = ExchangePayment.select(Exchange, ExchangePayment).join(Exchange) \
            .where(ExchangePayment.payment == payment.id)

        exchange_rates = self.exchange_service.get_exchange_rates(set([tx.date for tx in transactions]), ExchangeRate.Source.EXCHANGERATESIO)

        current_exchange = 0
        exchange_remaining = exchange_payments[current_exchange].amount

        for tx in transactions:
            amount = self.balance_service.calc_transaction_remaining(tx)
            remaining_amount = amount
            eur_usd_exchanged = 0

            while exchange_remaining < remaining_amount:
                eur_usd_exchanged += Decimal(exchange_remaining / remaining_amount) * exchange_payments[current_exchange].exchange.exchange_rate
                remaining_amount -= exchange_remaining
                current_exchange += 1
                exchange_remaining = exchange_payments[current_exchange].amount

            eur_usd_exchanged += Decimal(amount / remaining_amount) * exchange_payments[current_exchange].exchange.exchange_rate

            eur_usd_booked = exchange_rates[tx.date]
            ccy_risk, fx_fees = self.calc_fx_fees(tx.amount_usd, tx.amount_eur, eur_usd_booked, eur_usd_exchanged)

            tx.ccy_risk = ccy_risk
            tx.fx_fees = fx_fees
            tx.payment = payment.id
            tx.status_enum = Transaction.Status.PAID
            tx.save()

        avg_eur_usd_exchanged = 0
        for ep in exchange_payments:
            avg_eur_usd_exchanged += Decimal(ep.amount / payment.amount_usd) * ep.exchange.exchange_rate

        payment.amount_eur = round(payment.amount_usd / avg_eur_usd_exchanged)
        payment.processed = True
        payment.save()

        eur_sum = sum([tx.amount_eur + tx.ccy_risk + tx.fx_fees for tx in transactions])
        eur_err = payment.amount_eur - eur_sum

        # apply error to largest transaction
        largest_tx = max(transactions, key=lambda tx: tx.amount_usd)
        largest_tx.fx_fees += eur_err
        largest_tx.save()

        # in a separate loop:
        # update Actual transaction (set split amounts and clear) and update amounts as well!

        # create Actual transfer (add transfer split to exchange transaction)

    def calc_fx_fees(self, value_usd, value_eur, eur_usd_booked, eur_usd_exchanged):
        value_eur_exchanged = value_usd / eur_usd_exchanged
        effective_fees_total = value_eur_exchanged - value_eur

        ccy_risk = round(value_eur_exchanged - Decimal(value_usd / eur_usd_booked))

        # fx_fees_usd = value_usd - (eur_usd_booked * value_eur)
        # fx_fees = fx_fees_usd / eur_usd_exchanged
        fx_fees = round(effective_fees_total - ccy_risk)

        return ccy_risk, fx_fees