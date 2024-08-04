from backend.clients.mastercard import IMastercardClient
from backend.models import Transaction, ExchangeRate
from peewee import DoesNotExist
from flask_injector import inject


class ExchangeService:
    @inject
    def __init__(self, mastercard: IMastercardClient):
        self.mastercard = mastercard

    def add_missing_eur_amounts(self, account):
        transactions = Transaction.select().where((Transaction.account == account.id) & (Transaction.amount_eur.is_null()))
        if len(transactions) > 15:
            print("Too many transactions!")
            return

        exchange_rates = self.get_exchange_rates(set([tx.date for tx in transactions]), ExchangeRate.Source.MASTERCARD)

        for tx in transactions:
            tx.amount_eur = self.get_amount_eur(tx, exchange_rates)
            tx.save()

    def get_exchange_rates(self, dates, source: ExchangeRate.Source):
        return dict(zip(dates, [self.get_exchange_rate(date, source) for date in dates]))

    def get_exchange_rate(self, date, source: ExchangeRate.Source):
        try:
            return ExchangeRate.get(date=date, source=source.value).exchange_rate
        except DoesNotExist:
            if source == ExchangeRate.Source.MASTERCARD:
                return self.mastercard.get_conversion_rate(date)
            else:
                raise Exception("Not implemented")

    def get_amount_eur(self, tx, exchange_rates):
        date = tx.date
        if date not in exchange_rates or not exchange_rates[date]:
            return None
        else:
            return int(tx.amount_usd / exchange_rates[date])
