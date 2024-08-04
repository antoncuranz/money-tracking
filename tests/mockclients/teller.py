from backend.clients.teller import ITellerClient
from requests.exceptions import HTTPError

from tests.fixtures import ACCOUNT_1, TELLER_TX_1


class MockTellerClient(ITellerClient):
    def __init__(self):
        self.mfa_required = False
        self.mfa_error = {"error": {"code": "enrollment.disconnected.user_action.mfa_required"}}
        self.balances = {
            ACCOUNT_1["teller_id"]: {"available": "123.45", "ledger": "123.45"}
        }
        self.transactions = {
            ACCOUNT_1["teller_id"]: [TELLER_TX_1]
        }

    def get_account_balances(self, account):
        if self.mfa_required:
            return self.mfa_error

        if account.teller_id in self.balances:
            return {
                "account_id": account.teller_id,
                "available": self.balances[account.teller_id]["available"],
                "ledger": self.balances[account.teller_id]["ledger"]
            }
        else:
            raise HTTPError()

    def list_account_transactions(self, account):
        if self.mfa_required:
            return self.mfa_error

        if account.teller_id in self.transactions:
            return self.transactions[account.teller_id]
        else:
            raise HTTPError()

    def set_mfa_required(self, mfa_required: bool):
        self.mfa_required = mfa_required
