from requests.exceptions import HTTPError

from backend import ITellerClient
from backend.tests.fixtures import ACCOUNT_1, TELLER_TRANSACTIONS


class MockTellerClient(ITellerClient):
    def __init__(self):
        self.mfa_required = False
        self.mfa_error = {"error": {"code": "enrollment.disconnected.user_action.mfa_required"}}
        self.balances = {
            ACCOUNT_1["import_id"]: {"available": "123.45", "ledger": "123.45"}
        }
        self.transactions = {
            ACCOUNT_1["import_id"]: TELLER_TRANSACTIONS
        }

    def set_transactions(self, import_id, transactions):
        self.transactions[import_id] = transactions

    def get_account_balances(self, account):
        if self.mfa_required:
            return self.mfa_error

        if account.import_id in self.balances:
            return {
                "account_id": account.import_id,
                "available": self.balances[account.import_id]["available"],
                "ledger": self.balances[account.import_id]["ledger"]
            }
        else:
            raise HTTPError()

    def list_account_transactions(self, account):
        if self.mfa_required:
            return self.mfa_error

        if account.import_id in self.transactions:
            return self.transactions[account.import_id]
        else:
            raise HTTPError()

    def set_mfa_required(self, mfa_required: bool):
        self.mfa_required = mfa_required
