import requests

from models import ExchangeRate
from config import config


class IExchangeRateClient:
    def get_conversion_rate(self, date):
        raise NotImplementedError


class ExchangeratesApiIoClient(IExchangeRateClient):
    def __init__(self):
        self.access_key = config.exchangeratesio_access_key

    def get_conversion_rate(self, date):
        url = f"http://api.exchangeratesapi.io/v1/{date}?access_key={self.access_key}&base=EUR&symbols=USD"

        response = requests.get(url).json()
        return response["rates"]["USD"]


class MastercardClient(IExchangeRateClient):
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
            return response["data"]["conversionRate"]
        except Exception as error:
            print("Error retrieving conversion rate: ", error)
            return None  # TODO: raise?
