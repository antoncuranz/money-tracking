from backend.exchangerate.adapter.exchangerates_client import IExchangeRateClient


class MockExchangeRateClient(IExchangeRateClient):
    def __init__(self):
        self.rates = {
            "2024-01-01": 1.1,
            "2024-01-02": 1.2,
            "2024-01-03": 1.3,
            "2024-01-04": 1.0,
            "2024-01-05": 1.1,
        }

    def set_rates(self, rates):
        self.rates = rates

    def get_conversion_rate(self, date):
        if str(date) in self.rates:
            return self.rates[str(date)]
        else:
            return 1
