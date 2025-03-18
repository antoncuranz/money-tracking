import time
from decimal import Decimal
from typing import Annotated

import plaid
from fastapi import HTTPException, Depends
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.item_remove_request import ItemRemoveRequest
from sqlmodel import Session

from config import config
from data_import.dataaccess.dataimport_repository import DataImportRepository
from models import User, PlaidAccount


class PlaidService:
    def __init__(self, repository: Annotated[DataImportRepository, Depends()]):
        self.repository = repository
        configuration = plaid.Configuration(
            host=plaid.Environment.Production if config.plaid_environment == "production" else plaid.Environment.Sandbox,
            api_key={"clientId": config.plaid_client_id, "secret": config.plaid_secret, "plaidVersion": "2020-09-14"}
        )
        self.client = plaid_api.PlaidApi(plaid.ApiClient(configuration))

    def create_link_token(self):
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="Plaid Quickstart",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id=str(time.time()))
        )

        response = self.client.link_token_create(request)
        return response.to_dict()
    
    def exchange_token(self, session: Session, user: User, public_token: str):
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        exchange_response = self.client.item_public_token_exchange(exchange_request)
        
        connection = self.repository.create_plaid_connection(session, user, exchange_response.item_id, exchange_response.access_token)
        session.commit()
        
        self.discover_accounts(session, user, connection.id)
        return exchange_response.to_dict()
    
    def discover_accounts(self, session: Session, user: User, connection_id: int):
        connection = self.repository.get_plaid_connection(session, user, connection_id)
        if not connection:
            raise HTTPException(404)
        
        accounts_request = AccountsGetRequest(access_token=connection.plaid_access_token)
        accounts_response = self.client.accounts_get(accounts_request)
        
        connection.name = accounts_response.item.institution_name
        session.add(connection)
        
        for account in accounts_response.accounts:
            self.repository.get_or_create_plaid_account(session, account.account_id, {
                "name": account.name, "plaid_account_id": account.account_id, "connection_id": connection.id
            })
        session.commit()
    
    def get_account_balance(self, plaid_account: PlaidAccount):
        access_token = plaid_account.connection.plaid_access_token
        
        accounts_get_request = AccountsGetRequest(access_token=access_token)
        accounts_get_response = self.client.accounts_get(accounts_get_request)
        
        account = next(account for account in accounts_get_response["accounts"] if account["account_id"] == plaid_account.plaid_account_id)
        return int(Decimal(account["balances"]["current"] * 100).quantize(1))

    def sync_transactions(self, plaid_account: PlaidAccount):
        access_token = plaid_account.connection.plaid_access_token
        
        request = TransactionsSyncRequest(access_token=access_token, cursor=plaid_account.cursor if plaid_account.cursor else "")
        response = self.client.transactions_sync(request)
        
        added = response["added"]
        modified = response["modified"]
        removed = response["removed"]

        # the transactions in the response are paginated, so make multiple calls while incrementing the cursor to
        # retrieve all transactions
        while response["has_more"]:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=response["next_cursor"]
            )
            response = self.client.transactions_sync(request)
            added += response["added"]
            modified += response["modified"]
            removed += response["removed"]
        
        added = [tx for tx in added if tx.account_id == plaid_account.plaid_account_id]
        modified = [tx for tx in modified if tx.account_id == plaid_account.plaid_account_id]
        removed = [tx for tx in removed if tx.account_id == plaid_account.plaid_account_id]

        return added, modified, removed, response["next_cursor"]
    
    def get_connections(self, session: Session, user: User):
        return self.repository.get_plaid_connections(session, user)

    def delete_connection(self, session: Session, user: User, connection_id: int):
        connection = self.repository.get_plaid_connection(session, user, connection_id)
        if not connection:
            raise HTTPException(404)
        
        item_remove_request = ItemRemoveRequest(access_token=connection.plaid_access_token)
        self.client.item_remove(item_remove_request)
        
        session.delete(connection)
        session.commit()
