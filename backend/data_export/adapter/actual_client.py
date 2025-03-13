import abc
from typing import List, Optional

import requests

from config import config
from data_export.adapter import openapi
from models import Account, Transaction, User


class IActualClient(abc.ABC):
    @abc.abstractmethod
    def create_transaction(self, account: Account, transaction: openapi.Transaction):
        pass
    
    @abc.abstractmethod
    def create_transaction_super_misc(self, super_user: User, transaction: openapi.Transaction):
        pass

    @abc.abstractmethod
    def get_transaction(self, account: Account, tx: Transaction) -> Optional[openapi.Transaction]:
        pass

    @abc.abstractmethod
    def patch_transaction(self, account: Account, actual_tx: openapi.Transaction, updated_fields):
        pass

    @abc.abstractmethod
    def delete_transaction(self, user: User, actual_id: str):
        pass

    @abc.abstractmethod
    def get_payees(self, user: User) -> List[openapi.Payee]:
        pass

    @abc.abstractmethod
    def create_payee(self, user: User, payee_name: str) -> str:
        pass


class ActualClient(IActualClient):
    def __init__(self):
        self.api_key = config.actual_api_key
        self.base_url = config.actual_base_url


    def create_transaction(self, account: Account, transaction: openapi.Transaction):
        user = account.user
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/accounts/{account.actual_id}/transactions"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        payload = {
            "transaction": transaction.model_dump(exclude_unset=True)
        }

        response = requests.post(url, headers=headers, json=payload)

        if not response.ok:
            response.raise_for_status()


    def create_transaction_super_misc(self, super_user: User, transaction: openapi.Transaction):
        url = f"{self.base_url}/v1/budgets/{super_user.actual_sync_id}/accounts/{super_user.actual_misc_account}/transactions"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if super_user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = super_user.actual_encryption_password

        payload = {
            "transaction": transaction.model_dump(exclude_unset=True)
        }

        response = requests.post(url, headers=headers, json=payload)

        if not response.ok:
            response.raise_for_status()


    def get_transaction(self, account: Account, tx: Transaction) -> Optional[openapi.Transaction]:
        user = account.user
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/accounts/{account.actual_id}/transactions" \
              + f"?since_date={tx.date}&until_date={tx.date}"
        headers = {
            "x-api-key": self.api_key,
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        response = requests.get(url, headers=headers)

        if not response.ok:
            response.raise_for_status()
            
        data = response.json()["data"]
        
        found = next((actual_tx for actual_tx in data if actual_tx["id"] == tx.actual_id), None)
        if not found:
            return None
        
        return openapi.Transaction(**found)


    def patch_transaction(self, account: Account, actual_tx: openapi.Transaction, updated_fields):
        user = account.user
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/transactions/{actual_tx.id}"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        payload = {
            "transaction": actual_tx.model_dump(exclude_unset=True, exclude={"subtransactions"}) | updated_fields
        }

        response = requests.patch(url, headers=headers, json=payload)

        if not response.ok:
            response.raise_for_status()


    def delete_transaction(self, user: User, actual_id: str):
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/transactions/{actual_id}"
        headers = {
            'x-api-key': self.api_key
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        response = requests.delete(url, headers=headers)

        if not response.ok:
            response.raise_for_status()


    def get_payees(self, user: User) -> List[openapi.Payee]:
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/payees"
        headers = {
            "x-api-key": self.api_key,
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        response = requests.get(url, headers=headers)

        if not response.ok:
            response.raise_for_status()

        return [openapi.Payee(**payee) for payee in response.json()["data"]]


    def create_payee(self, user: User, payee_name: str) -> str:
        url = f"{self.base_url}/v1/budgets/{user.actual_sync_id}/payees"
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        if user.actual_encryption_password is not None:
            headers["budget-encryption-password"] = user.actual_encryption_password

        payload = dict(payee=dict(name=payee_name))

        response = requests.post(url, headers=headers, json=payload)

        if not response.ok:
            response.raise_for_status()

        return response.json()["data"]
