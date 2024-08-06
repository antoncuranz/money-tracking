import datetime
import ibind
import urllib3
from flask_injector import inject

from backend.clients.exchangerates import IExchangeRateClient

urllib3.disable_warnings()

# https://pennies.interactivebrokers.com/cstools/contract_info/v3.10/index.php
CONID_EUR = "12087792"
CONID_CHF = "12087802"
BUY_USD = "SELL"
SELL_USD = "BUY"


class IbkrClient(IExchangeRateClient):
    @inject
    def __init__(self, host, port):
        self._client = ibind.IbkrClient(host=host, port=port)
        self._account_id = self._get_account_id()

        if not self._client.check_health():
            print("Error: healthcheck failed")
            exit(1)

    def _get_account_id(self):
        accounts = self._client.portfolio_accounts().data
        if len(accounts) > 1:
            print("Error: more than one account present")
            exit(1)

        return accounts[0]["id"]

    def print_settled_cash(self):
        print("\n#### settled cash ####")
        ledger = self._client.get_ledger(self._account_id).data
        for k, v in ledger.items():
            if k == "BASE":
                continue
            print(f"{k}: {v["settledcash"]}")

        new_usd = ledger["USD"]["settledcash"]
        # bought = round(new_usd - old_usd, 2)

    def exchange_money(self, quantity, conid=CONID_EUR, side=BUY_USD):
        print("\n### exchanging money ###")
        print(self._client.contract_information_by_conid(conid))
        order_tag = f'my_order-{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}'

        order_request = {
            "acctId": self._account_id,
            "cOID": order_tag,
            "conid": conid,
            "quantity": quantity - 2,  # TODO
            # "fxQty": 200,
            "isCcyConv": True,
            "orderType": "MKT",
            "side": side,
            "tif": "DAY",
        }

        answers = {
            "understanding cash quantity details": True
        }

        response = self._client.place_order(order_request, answers, self._account_id).data
        print(response)
        # print(f"Bought {bought} USD for {quantity}€") # TODO

    def historical_data(self, date, conid):
        rsp = self._client.marketdata_history_by_conid(conid, start_time=date, period="1y", bar="1d").data
        market_data = []
        for dp in rsp["data"]:
            date = datetime.datetime.fromtimestamp(dp["t"] / 1000)
            market_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "marketPrice": dp["c"]
            })

        return market_data

    def historical_forex_data(self, start_time, conid=CONID_EUR):
        print(start_time)
        rsp = self._client.marketdata_history_by_conid(conid, start_time=start_time, period="1m", bar="1d").data
        # print(rsp)
        avg_month = 0
        for dp in rsp["data"]:
            # print(f"{}")
            # print(datetime.datetime.fromtimestamp(dp["t"]/1000, datetime.UTC).strftime('%Y-%m-%d %H:%M:%S'))
            avg_day = dp["l"] + (dp["h"] - dp["l"]) / 2
            # print(f"avg_day: {avg_day}")
            avg_month = avg_month + avg_day
        avg_month = avg_month / len(rsp["data"])
        last_day_diff = avg_day - avg_month
        print(
            f"last_day: {avg_day}; avg_month: {avg_month}; last_day_diff: {last_day_diff}; 500€: {last_day_diff * 500}; 1000€: {last_day_diff * 1000}")
        return last_day_diff * 1000
