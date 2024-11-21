import requests
from flask_injector import inject


class IActualClient:
    def create_transaction(self, account_id, transaction):
        raise NotImplementedError

    def get_transaction(self, account_id, tx):
        raise NotImplementedError

    def patch_transaction(self, account_id, actual_tx, updated_fields):
        raise NotImplementedError

    def delete_transaction(self, actual_id):
        raise NotImplementedError

    def get_payees(self):
        raise NotImplementedError

    # def get_payee(self, payee_id):
    #     raise NotImplementedError

    def create_payee(self, payee_name):
        raise NotImplementedError

    # def update_payee(self, payee_id, payee_name):
    #     raise NotImplementedError


class ActualClient(IActualClient):
    @inject
    def __init__(self, api_key, budget_sync_id, base_url, encryption_passwd=None):
        self.api_key = api_key
        self.budget_sync_id = budget_sync_id
        self.base_url = base_url
        self.encryption_passwd = encryption_passwd

    def create_transaction(self, account_id, transaction):
        url = f"{self.base_url}/v1/budgets/{self.budget_sync_id}/accounts/{account_id}/transactions"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if self.encryption_passwd is not None:
            headers["budget-encryption-password"] = self.encryption_passwd

        payload = {
            "transaction": transaction
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def get_transaction(self, account_id, tx):
        url = f"{self.base_url}/v1/budgets/{self.budget_sync_id}/accounts/{account_id}/transactions" \
              + f"?since_date={tx.date}&until_date={tx.date}"
        headers = {
            "x-api-key": self.api_key,
        }
        if self.encryption_passwd is not None:
            headers["budget-encryption-password"] = self.encryption_passwd

        response = requests.get(url, headers=headers)

        if response.ok:
            data = response.json()["data"]
            return next(actual_tx for actual_tx in data if actual_tx["id"] == tx.actual_id)
        else:
            response.raise_for_status()

    def patch_transaction(self, account_id, actual_tx, updated_fields):
        url = f"{self.base_url}/v1/budgets/{self.budget_sync_id}/transactions/{actual_tx["id"]}"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if self.encryption_passwd is not None:
            headers["budget-encryption-password"] = self.encryption_passwd

        payload = {
            "transaction": actual_tx | updated_fields
        }

        response = requests.patch(url, headers=headers, json=payload)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def delete_transaction(self, actual_id):
        url = f"{self.base_url}/v1/budgets/{self.budget_sync_id}/transactions/{actual_id}"
        headers = {
            'x-api-key': self.api_key
        }
        if self.encryption_passwd is not None:
            headers["budget-encryption-password"] = self.encryption_passwd

        response = requests.delete(url, headers=headers)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()
            
    def get_payees(self):
        url = f"{self.base_url}/v1/budgets/{self.budget_sync_id}/payees"
        headers = {
            "x-api-key": self.api_key,
        }
        if self.encryption_passwd is not None:
            headers["budget-encryption-password"] = self.encryption_passwd

        response = requests.get(url, headers=headers)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()
            
    def get_payee(self, payee_id):
        url = f"{self.base_url}/v1/budgets/{self.budget_sync_id}/payees/{payee_id}"
        headers = {
            "x-api-key": self.api_key,
        }
        if self.encryption_passwd is not None:
            headers["budget-encryption-password"] = self.encryption_passwd

        response = requests.get(url, headers=headers)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def create_payee(self, payee_name):
        url = f"{self.base_url}/v1/budgets/{self.budget_sync_id}/payees"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if self.encryption_passwd is not None:
            headers["budget-encryption-password"] = self.encryption_passwd

        payload = dict(payee=dict(name=payee_name))

        response = requests.post(url, headers=headers, json=payload)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()
            
    def update_payee(self, payee_id, payee_name):
        url = f"{self.base_url}/v1/budgets/{self.budget_sync_id}/payees/{payee_id}"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if self.encryption_passwd is not None:
            headers["budget-encryption-password"] = self.encryption_passwd

        payload = dict(payee=dict(name=payee_name))

        response = requests.patch(url, headers=headers, json=payload)

        if response.ok:
            return response.json()
        else:
            response.raise_for_status()
