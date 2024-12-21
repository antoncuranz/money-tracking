from flask_injector import inject
from decimal import Decimal

from backend.models import Transaction, db, Exchange, ExchangePayment, Payment, Account
from backend.core.service.balance_service import BalanceService
from backend.core.service.exchange_service import ExchangeService
from backend.data_export.actual_service import ActualService


class PaymentService:
    @inject
    def __init__(self, balance_service: BalanceService, exchange_service: ExchangeService, actual_service: ActualService):
        self.balance_service = balance_service
        self.exchange_service = exchange_service
        self.actual_service = actual_service
    
    def get_payments(self, user, account_id, processed=None):
        query = (Account.user == user.id)

        if processed is not None:
            query = query & (Payment.status == Payment.Status.PROCESSED.value if processed else Payment.status != Payment.Status.PROCESSED.value)

        if account_id is not None:
            query = query & (Payment.account == account_id)

        return Payment.select().join(Account).where(query).order_by(-Payment.date)
        
    def process_payment(self, user, payment_id, transactions=None):
        """
        Raises
        ------
        DoesNotExist
            If a payment with the given `payment_id` does not exist or does not belong to the given `user`.
        """
        payment = Payment.get(Payment.id == payment_id)
        account = Account.get((Account.user == user.id) & (Account.id == payment.account))

        if not transactions:
            transactions = self._guess_transactions_to_process(payment)
        
        processed_transactions = self._process_payment(payment, transactions)
        
        self.actual_service.update_transactions(account, processed_transactions)
        self.actual_service.export_payment(account, payment)
    
    def unprocess_payment(self, user, payment_id):
        payment = Payment.get(Payment.id == payment_id)
        account = Account.get((Account.user == user.id) & (Account.id == payment.account))

        transactions = Transaction.select().where(
            (Transaction.account == account.id) &
            (Transaction.payment == payment_id) &
            (Transaction.status == Transaction.Status.PAID.value)
        )
        for tx in transactions:
            tx.status_enum = Transaction.Status.POSTED
            tx.payment = None
            tx.fees_and_risk_eur = None
            tx.save()

        payment.status_enum = Payment.Status.POSTED
        payment.amount_eur = None
        payment.actual_id = None
        payment.save()

        self.actual_service.update_transactions(account, transactions)
        if payment.actual_id is not None:
            self.actual_service.delete_transaction(account.user, payment.actual_id)

    def _guess_transactions_to_process(self, payment):
        transactions = Transaction.select().where(
            (Transaction.status == Transaction.Status.POSTED.value) &
            (Transaction.account == payment.account)
        ).order_by(Transaction.date)  # TODO: order by date, then id

        process_tx = []
        amount = payment.amount_usd

        for tx in transactions:
            tx_remaining = self.balance_service.calc_transaction_remaining(tx)
            if 0 < amount < tx_remaining:
                raise Exception("Error finding transactions automatically.")

            if amount > 0:
                process_tx.append(tx)
                amount -= tx_remaining
            else:
                break

        return process_tx

    @db.atomic()
    def _process_payment(self, payment, transactions):
        if payment.status_enum == Payment.Status.PENDING:
            raise Exception("Error: Payment is still pending!")

        if payment.status_enum == Payment.Status.PROCESSED or len(payment.transactions) > 0:
            raise Exception("Error: Payment was already processed!")

        tx_remaining_sum = sum([self.balance_service.calc_transaction_remaining(tx) for tx in transactions])
        if payment.amount_usd != tx_remaining_sum:
            raise Exception("Error: Payment amount does not match sum of transactions!")

        exchange_payments = ExchangePayment.select(Exchange, ExchangePayment).join(Exchange) \
            .where(ExchangePayment.payment == payment.id)

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

            if remaining_amount != 0:
                eur_usd_exchanged += Decimal(remaining_amount / amount) * exchange_payments[current_exchange].exchange.exchange_rate
                exchange_remaining -= remaining_amount

                tx.fees_and_risk_eur = self.calc_fees_and_risk(tx.amount_usd, tx.amount_eur, eur_usd_exchanged)
            else:
                tx.fees_and_risk_eur = 0

            tx.payment = payment.id
            tx.status_enum = Transaction.Status.PAID
            tx.save()

        avg_eur_usd_exchanged = 0
        for ep in exchange_payments:
            avg_eur_usd_exchanged += Decimal(ep.amount / payment.amount_usd) * ep.exchange.exchange_rate

        payment.amount_eur = round(payment.amount_usd / avg_eur_usd_exchanged)
        payment.status_enum = Payment.Status.PROCESSED
        payment.save()

        eur_sum = sum([tx.amount_eur + tx.fees_and_risk_eur for tx in transactions])
        eur_err = payment.amount_eur - eur_sum
        print("Calculated eur_err of " + str(eur_err))

        # apply error to largest transaction
        largest_tx = max(transactions, key=lambda tx: tx.amount_usd)
        largest_tx.fees_and_risk_eur += eur_err
        largest_tx.save()

    def calc_fees_and_risk(self, value_usd, value_eur, eur_usd_exchanged):
        value_eur_exchanged = value_usd / eur_usd_exchanged
        effective_fees_total = value_eur_exchanged - value_eur

        return round(effective_fees_total)
