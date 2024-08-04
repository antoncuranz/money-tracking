import requests
from flask_injector import inject


class IActualClient:
    def import_transactions(self, account_id, transactions):
        raise NotImplementedError


class ActualClient(IActualClient):
    @inject
    def __init__(self, api_key, budget_sync_id, base_url="http://localhost:5007"):
        self.api_key = api_key
        self.budget_sync_id = budget_sync_id
        self.base_url = base_url

    def get_transactions(self, account_id, since_date):
        url = f"{self.base_url}/v1/budgets/{self.budget_sync_id}/accounts/{account_id}/transactions?since_date={since_date}"
        headers = {
            'x-api-key': self.api_key,
        }

        response = requests.get(url, headers=headers)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def import_transactions(self, account_id, transactions):
        url = f"{self.base_url}/v1/budgets/{self.budget_sync_id}/accounts/{account_id}/transactions/import"
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
        }
        payload = {
            "transactions": transactions
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def patch_transaction(self, transaction_id, transaction):
        url = f"{self.base_url}/v1/budgets/{self.budget_sync_id}/transactions/{transaction_id}"
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
        }
        payload = {
            "transaction": transaction
        }

        response = requests.patch(url, headers=headers, json=payload)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()
