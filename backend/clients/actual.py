import requests
from flask_injector import inject


class IActualClient:
    def create_transaction(self, account, transaction):
        raise NotImplementedError

    def get_transaction(self, account, tx):
        raise NotImplementedError

    def patch_transaction(self, account, actual_tx, updated_fields):
        raise NotImplementedError

    def delete_transaction(self, user, actual_id):
        raise NotImplementedError

    def get_payees(self, user):
        raise NotImplementedError

    def create_payee(self, user, payee_name):
        raise NotImplementedError


class ActualClient(IActualClient):
    @inject
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    def create_transaction(self, account, transaction):
        user = account.user
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/accounts/{account.actual_id}/transactions"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        payload = {
            "transaction": transaction
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def get_transaction(self, account, tx):
        user = account.user
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/accounts/{account.actual_id}/transactions" \
              + f"?since_date={tx.date}&until_date={tx.date}"
        headers = {
            "x-api-key": self.api_key,
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        response = requests.get(url, headers=headers)

        if response.ok:
            data = response.json()["data"]
            return next(actual_tx for actual_tx in data if actual_tx["id"] == tx.actual_id)
        else:
            response.raise_for_status()

    def patch_transaction(self, account, actual_tx, updated_fields):
        user = account.user
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/transactions/{actual_tx["id"]}"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        payload = {
            "transaction": actual_tx | updated_fields
        }

        response = requests.patch(url, headers=headers, json=payload)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def delete_transaction(self, user, actual_id):
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/transactions/{actual_id}"
        headers = {
            'x-api-key': self.api_key
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        response = requests.delete(url, headers=headers)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()
            
    def get_payees(self, user):
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/payees"
        headers = {
            "x-api-key": self.api_key,
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        response = requests.get(url, headers=headers)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def create_payee(self, user, payee_name):
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/payees"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        payload = dict(payee=dict(name=payee_name))

        response = requests.post(url, headers=headers, json=payload)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()
