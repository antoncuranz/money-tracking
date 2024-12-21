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
        
        self._process_payment(payment, transactions)
        
        self.actual_service.update_transactions(account, transactions)
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

        avg_eur_usd_exchanged, neutral_ratio = self._calc_avg_todo(payment, exchange_payments, transactions)

        for tx in transactions:
            amount = self.balance_service.calc_transaction_remaining(tx)

            if tx.neutral: # TODO: what value does a neutral tx have for amount_eur? The avg one!
                tx.fees_and_risk_eur = 0
            else:
                tx.fees_and_risk_eur = self._calc_fees_and_risk(amount, tx.amount_eur, avg_eur_usd_exchanged) / (1 - neutral_ratio) # TODO: do we need this?

            tx.payment = payment.id
            tx.status_enum = Transaction.Status.PAID
            tx.save()

        payment.amount_eur = round(payment.amount_usd / avg_eur_usd_exchanged)
        payment.status_enum = Payment.Status.PROCESSED
        payment.save()

        eur_sum = sum([tx.amount_eur + tx.fees_and_risk_eur for tx in transactions])
        eur_err = payment.amount_eur - eur_sum
        print("Calculated eur_err of " + str(eur_err)) # TODO: send notification or display in frontend

        # apply error to largest transaction
        largest_tx = max(transactions, key=lambda tx: tx.amount_usd if not tx.neutral else 0)
        largest_tx.fees_and_risk_eur += eur_err
        largest_tx.save()

    def _calc_fees_and_risk(self, value_usd, value_eur, eur_usd_exchanged):
        value_eur_exchanged = value_usd / eur_usd_exchanged
        effective_fees_total = value_eur_exchanged - value_eur

        return round(effective_fees_total)

    def _calc_avg_todo(self, payment, exchange_payments, transactions):
        avg_eur_usd_exchanged = 0
        neutral_sum = 0
        for ep in exchange_payments:
            if ep.exchange.neutral:
                neutral_sum += ep.amount
            else:
                avg_eur_usd_exchanged += Decimal(ep.amount / payment.amount_usd) * ep.exchange.exchange_rate
        neutral_ratio = Decimal(neutral_sum / payment.amount_usd)
        avg_eur_usd_exchanged = avg_eur_usd_exchanged / (1 - neutral_ratio)

        if neutral_sum != sum(self.balance_service.calc_transaction_remaining(tx) for tx in transactions if tx.neutral):
            raise Exception("Error: neutral sum differs between Transactions and Exchanges!")

        return avg_eur_usd_exchanged, neutral_ratio
