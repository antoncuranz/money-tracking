import requests

from backend import ExchangeRate


class IMastercardClient:
    def get_conversion_rate(self, date):
        raise NotImplementedError


class MastercardClient(IMastercardClient):
    _URL = "https://www.mastercard.de/settlement/currencyrate/conversion-rate"

    def get_conversion_rate(self, date):
        params = {
            "fxDate": str(date),
            "transCurr": "EUR",
            "crdhldBillCurr": "USD",
            "bankFee": 0,
            "transAmt": 100
        }

        try:
            response = requests.get(self._URL, params=params).json()
            rate = response["data"]["conversionRate"]
            ExchangeRate.create(date=date, source=ExchangeRate.Source.MASTERCARD.value, exchange_rate=rate)
            return rate
        except Exception as error:
            print("Error retrieving conversion rate: ", error)
            return None  # TODO: raise?
