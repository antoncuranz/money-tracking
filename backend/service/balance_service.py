from flask_injector import inject

from backend.models import ExchangePayment, Exchange, Credit, CreditTransaction


class BalanceService:
    @inject
    def __init__(self):
        pass

    def calc_balance_exchanged(self):
        balance = 0

        for exchange in Exchange.select():
            balance += self.calc_exchange_remaining(exchange)

        return balance

    def calc_exchange_remaining(self, exchange: Exchange):
        balance = exchange.amount_usd

        query = ExchangePayment.select().where(ExchangePayment.exchange == exchange)

        for exchange_payment in query:
            balance += exchange_payment.amount

        if balance < 0:
            raise Exception(f"Error: Exchange balance for exchange {exchange.id} is negative!")

        return balance

    def calc_balance_credits(self):
        balance = 0

        for credit in Credit.select():
            balance += self.calc_credit_remaining(credit)

        return balance

    def calc_credit_remaining(self, credit: Credit):
        balance = credit.amount_usd

        query = CreditTransaction.select().where(CreditTransaction.credit == credit.id)

        for credit_transaction in query:
            balance -= credit_transaction.amount

        if balance < 0:
            raise Exception(f"Error: Credit balance for credit {credit.id} is negative!")

        return balance
