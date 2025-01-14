import datetime

from backend.data_import.adapter.quiltt_client import IQuilttClient
from backend.tests.fixtures import ACCOUNT_1, QUILTT_TRANSACTIONS


class MockQuilttClient(IQuilttClient):
    def __init__(self):
        self.balances = {
            ACCOUNT_1["import_id"]: 123.45
        }
        self.transactions = {
            ACCOUNT_1["import_id"]: QUILTT_TRANSACTIONS
        }

    def set_transactions(self, import_id, transactions):
        self.transactions[import_id] = transactions

    def get_account_transactions(self, account_import_id, token):
        if token is None:
            raise RuntimeError("Invalid Token (mocked)")

        if account_import_id in self.transactions:
            return self.transactions[account_import_id]
        else:
            raise RuntimeError("Not Found (mocked)")

    def get_account_balance(self, account_import_id, token):
        if token is None:
            raise RuntimeError("Invalid Token (mocked)")

        if account_import_id in self.balances:
            return self.balances[account_import_id]
        else:
            raise RuntimeError("Not Found (mocked)")

    def retrieve_session_token(self):
        return "MOCK_TOKEN", datetime.datetime.now() + datetime.timedelta(days=1)
