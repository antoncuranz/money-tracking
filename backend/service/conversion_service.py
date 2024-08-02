from backend.models import Transaction
import requests
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

        conversion_rates = self.get_conversion_rates([str(tx.date) for tx in transactions])

        for tx in transactions:
            tx.amount_eur = self.get_amount_eur(tx, conversion_rates)
            tx.save()

    def get_conversion_rates(self, dates):
        return dict(zip(dates, [self.get_conversion_rate(date) for date in dates]))

    def get_conversion_rate(self, date):
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
            return response["data"]["conversionRate"]
        except Exception as error:
            print("Error retrieving conversion rate: ", error)
            return None

    def get_amount_eur(self, tx, conversion_rates):
        date = str(tx.date)
        if date not in conversion_rates or not conversion_rates[date]:
            return None
        else:
            return int(tx.amount_usd / conversion_rates[date])
