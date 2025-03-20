import datetime

from plaid.api import plaid_api
from plaid.model.account_balance import AccountBalance
from plaid.model.account_base import AccountBase
from plaid.model.accounts_get_response import AccountsGetResponse
from plaid.model.item import Item
from plaid.model.transactions_sync_response import TransactionsSyncResponse
from plaid.model.transaction import Transaction
from plaid.model.removed_transaction import RemovedTransaction

from data_import.business.plaid_service import PlaidService
from models import User, PlaidConnection, PlaidAccount
from tests.fixtures import *

def _create_plaid_tx(account_id: str, amount: float, transaction_id: str, date: datetime.date, pending: bool):
    return Transaction(account_id=account_id, amount=amount, iso_currency_code=None, unofficial_currency_code=None,
                       category=None, category_id=None, date=date, location=None, name="Description", merchant_name="Merchant Name",
                       payment_meta=None, pending=pending, pending_transaction_id=None, account_owner=None,
                       transaction_id=transaction_id, authorized_date=None, authorized_datetime=None, datetime=None,
                       payment_channel=None, transaction_code=None, counterparties=[], _check_type=False)

def test_discover_accounts(mocker):
    # Arrange
    session = mocker.Mock()

    user = User(id=1, name="alice", super_user=True)
    connection = PlaidConnection(**PLAID_CONNECTION_1)
    accounts = [
        AccountBase(account_id="plaid-account-1", name="Plaid Account 1", balances=None, mask=None,
                    official_name="Official Plaid Account 1", type=None, subtype=None, _check_type=False),
        AccountBase(account_id="plaid-account-2", name="Plaid Account 2", balances=None, mask=None,
                    official_name="Official Plaid Account 2", type=None, subtype=None, _check_type=False)
    ]
    item = Item(item_id="plaid-item-1", institution_name="Plaid Institution", webhook=None, error=None,
                available_products=None, billed_products=None, consent_expiration_time=None, update_type=None,
                _check_type=False)

    accounts_get_mock = mocker.Mock()
    accounts_get_mock.return_value = AccountsGetResponse(accounts=accounts, item=item, request_id="request-1")
    mocker.patch.object(plaid_api.PlaidApi, "accounts_get", accounts_get_mock)

    repository_mock = mocker.Mock()
    repository_mock.get_plaid_connection.return_value = connection
    under_test = PlaidService(repository_mock)

    # Act
    under_test.discover_accounts(session=session, user=user, connection_id=1)

    # Assert
    assert repository_mock.get_or_create_plaid_account.call_count == len(accounts)
    call_args_list = repository_mock.get_or_create_plaid_account.call_args_list

    for idx, call in enumerate(call_args_list):
        assert call.args[0] == session
        assert call.args[1] == accounts[idx].account_id
        assert call.args[2]["name"] == accounts[idx].name
        assert call.args[2]["plaid_account_id"] == accounts[idx].account_id
        assert call.args[2]["connection_id"] == connection.id

    session.add.assert_called_with(connection)
    session.commit.assert_called_once()


def test_get_account_balance(mocker):
    # Arrange
    plaid_account = PlaidAccount(**PLAID_ACCOUNT_2)
    plaid_account.connection = PlaidConnection(**PLAID_CONNECTION_1)

    accounts = [
        AccountBase(account_id="plaid-account-1", name="Plaid Account 1",
                    balances=AccountBalance(current=12.34, available=None, limit=None, iso_currency_code=None,
                                            unofficial_currency_code=None), mask=None,
                    official_name="Official Plaid Account 1", type=None, subtype=None, _check_type=False),
        AccountBase(account_id="plaid-account-2", name="Plaid Account 2",
                    balances=AccountBalance(current=43.21, available=None, limit=None, iso_currency_code=None,
                                            unofficial_currency_code=None), mask=None,
                    official_name="Official Plaid Account 2", type=None, subtype=None, _check_type=False)
    ]
    accounts_get_response = AccountsGetResponse(accounts=accounts, item=None, request_id="request-1", _check_type=False)

    accounts_get_mock = mocker.Mock()
    accounts_get_mock.return_value = accounts_get_response
    mocker.patch.object(plaid_api.PlaidApi, "accounts_get", accounts_get_mock)

    repository_mock = mocker.Mock()
    under_test = PlaidService(repository_mock)

    # Act & Assert
    assert under_test.get_account_balance(plaid_account) == 4321


def test_sync_transactions(mocker):
    # Arrange
    plaid_account = PlaidAccount(**PLAID_ACCOUNT_1)
    plaid_account.connection = PlaidConnection(**PLAID_CONNECTION_1)

    added = [
        _create_plaid_tx(account_id="plaid-account-1", amount=12.34, date=datetime.date(2025, 1, 1), pending=False, transaction_id="plaid-tx-1"),
        _create_plaid_tx(account_id="plaid-account-1", amount=43.21, date=datetime.date(2025, 1, 2), pending=False, transaction_id="plaid-tx-2"),
        _create_plaid_tx(account_id="plaid-account-1", amount=12.34, date=datetime.date(2025, 1, 3), pending=True, transaction_id="plaid-tx-3"),
        _create_plaid_tx(account_id="plaid-account-2", amount=12.34, date=datetime.date(2025, 1, 2), pending=False, transaction_id="plaid-tx-4")
    ]
    modified = added
    removed = [
        RemovedTransaction(transaction_id="removed-tx-1", account_id="plaid-account-1"),
        RemovedTransaction(transaction_id="removed-tx-2", account_id="plaid-account-2"),
        RemovedTransaction(transaction_id="removed-tx-3", account_id="plaid-account-2")
    ]

    sync_response_1 = TransactionsSyncResponse(transactions_update_status=None, accounts=[], added=[added[0]], modified=[modified[0]], removed=[removed[0]], next_cursor="cursor-2", has_more=True, request_id="request-1", _check_type=False)
    sync_response_2 = TransactionsSyncResponse(transactions_update_status=None, accounts=[], added=[added[1]], modified=[modified[1]], removed=[removed[1]], next_cursor="cursor-3", has_more=True, request_id="request-2", _check_type=False)
    sync_response_3 = TransactionsSyncResponse(transactions_update_status=None, accounts=[], added=added[2:], modified=modified[2:], removed=removed[2:], next_cursor="cursor-4", has_more=False, request_id="request-3", _check_type=False)

    sync_response_mock = mocker.Mock()
    sync_response_mock.side_effect = [sync_response_1, sync_response_2, sync_response_3]
    mocker.patch.object(plaid_api.PlaidApi, "transactions_sync", sync_response_mock)

    repository_mock = mocker.Mock()
    under_test = PlaidService(repository_mock)

    # Act
    actual_added, actual_modified, actual_removed, next_cursor = under_test.sync_transactions(plaid_account)
    
    # Assert
    assert sync_response_mock.call_count == 3
    cursors = [call[0][0].cursor for call in sync_response_mock.call_args_list]
    assert cursors == ["cursor-1", "cursor-2", "cursor-3"]
    
    assert actual_added == [tx for tx in added if tx.account_id == "plaid-account-1"]
    assert actual_modified == [tx for tx in modified if tx.account_id == "plaid-account-1"]
    assert actual_removed == [tx for tx in removed if tx.account_id == "plaid-account-1"]
    assert next_cursor == "cursor-4"

