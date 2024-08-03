from backend.models import Transaction, ExchangeRate
import requests
from peewee import DoesNotExist
from flask_injector import inject


class ConversionService:
    @inject
    def __init__(self):
        pass

    def add_missing_eur_amounts(self, account):
        transactions = Transaction.select().where((Transaction.account == account.id) & (Transaction.amount_eur.is_null()))
        if len(transactions) > 15:
            print("Too many transactions!")
            return

        conversion_rates = self.get_conversion_rates(set([tx.date for tx in transactions]), ExchangeRate.Source.MASTERCARD)

        for tx in transactions:
            tx.amount_eur = self.get_amount_eur(tx, conversion_rates)
            tx.save()

    def get_conversion_rates(self, dates, source: ExchangeRate.Source):
        return dict(zip(dates, [self.get_conversion_rate(date, source) for date in dates]))

    def get_conversion_rate(self, date, source: ExchangeRate.Source):
        try:
            return ExchangeRate.get(date=date, source=source.value).exchange_rate
        except DoesNotExist:
            if source == ExchangeRate.Source.MASTERCARD:
                return self.fetch_mastercard_conversion_rate(date)
            else:
                raise Exception("Not implemented")

    def fetch_mastercard_conversion_rate(self, date):
        url = "https://www.mastercard.de/settlement/currencyrate/conversion-rate"
        params = {
            "fxDate": str(date),
            "transCurr": "EUR",
            "crdhldBillCurr": "USD",
            "bankFee": 0,
            "transAmt": 100
        }

        try:
            response = requests.get(url, params=params).json()
            rate = response["data"]["conversionRate"]
            ExchangeRate.create(date=date, source=ExchangeRate.Source.MASTERCARD.value, exchange_rate=rate)
            return rate
        except Exception as error:
            print("Error retrieving conversion rate: ", error)
            return None

    def get_amount_eur(self, tx, conversion_rates):
        date = tx.date
        if date not in conversion_rates or not conversion_rates[date]:
            return None
        else:
            return int(tx.amount_usd / conversion_rates[date])
