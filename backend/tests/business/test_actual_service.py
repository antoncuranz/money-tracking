from config import config
from data_export.business.actual_service import ActualService
from models import Transaction
from tests.fixtures import *

ACTUAL_TRANSACTIONS = {
    "id": 1,
    "payee": "payee_1",
    "subtransactions": [
        {"id": 2, "category": None},
        {"id": 3, "category": config.actual_fee_category}
    ]
}


def test_update_transaction(mocker):
    # Arrange
    repository_mock = mocker.Mock()
    account = mocker.Mock()
    repository_mock.get_account.return_value = account
    
    actual_mock = mocker.Mock()
    actual_mock.get_transaction.return_value = ACTUAL_TRANSACTIONS

    under_test = ActualService(actual_mock, None, repository_mock)
    
    tx = Transaction(**TX_1)
    tx.actual_id = "something"

    # Act
    under_test.update_transaction(session=None, user=None, account_id=1, tx=tx, existing_payees={})
    
    # Assert
    assert actual_mock.patch_transaction.call_count == 3
    call_args_list = actual_mock.patch_transaction.call_args_list
    
    main_tx_call = call_args_list[0].args
    assert main_tx_call[0] == account
    assert main_tx_call[1]["id"] == 1
    assert main_tx_call[2]["amount"] == -tx.amount_eur
    
    main_split_call = call_args_list[1].args
    assert main_split_call[0] == account
    assert main_split_call[1]["id"] == 2
    assert main_split_call[2]["amount"] == -tx.amount_eur
    
    fx_split_call = call_args_list[2].args
    assert fx_split_call[0] == account
    assert fx_split_call[1]["id"] == 3
    assert fx_split_call[2]["amount"] == 0
    
    
def test_update_transaction_null_amount_eur(mocker):
    # Arrange
    repository_mock = mocker.Mock()
    account = mocker.Mock()
    repository_mock.get_account.return_value = account

    actual_mock = mocker.Mock()
    actual_mock.get_transaction.return_value = ACTUAL_TRANSACTIONS
    
    exchangerate_mock = mocker.Mock()
    exchangerate_mock.guess_amount_eur.return_value = 1234

    under_test = ActualService(actual_mock, exchangerate_mock, repository_mock)

    tx = Transaction(**TX_1)
    tx.actual_id = "something"
    tx.amount_eur = None

    # Act
    under_test.update_transaction(session=None, user=None, account_id=1, tx=tx, existing_payees={})

    # Assert
    assert actual_mock.patch_transaction.call_count == 3
    call_args_list = actual_mock.patch_transaction.call_args_list

    main_tx_call = call_args_list[0].args
    assert main_tx_call[0] == account
    assert main_tx_call[1]["id"] == 1
    assert main_tx_call[2]["amount"] == -1234

    main_split_call = call_args_list[1].args
    assert main_split_call[0] == account
    assert main_split_call[1]["id"] == 2
    assert main_split_call[2]["amount"] == -1234

    fx_split_call = call_args_list[2].args
    assert fx_split_call[0] == account
    assert fx_split_call[1]["id"] == 3
    assert fx_split_call[2]["amount"] == 0


def test_update_transaction_zero_amount_eur(mocker):
    # Arrange
    repository_mock = mocker.Mock()
    account = mocker.Mock()
    repository_mock.get_account.return_value = account

    actual_mock = mocker.Mock()
    actual_mock.get_transaction.return_value = ACTUAL_TRANSACTIONS

    under_test = ActualService(actual_mock, None, repository_mock)

    tx = Transaction(**TX_1)
    tx.actual_id = "something"
    tx.amount_eur = 0

    # Act
    under_test.update_transaction(session=None, user=None, account_id=1, tx=tx, existing_payees={})

    # Assert
    assert actual_mock.patch_transaction.call_count == 3
    call_args_list = actual_mock.patch_transaction.call_args_list

    main_tx_call = call_args_list[0].args
    assert main_tx_call[0] == account
    assert main_tx_call[1]["id"] == 1
    assert main_tx_call[2]["amount"] == 0

    main_split_call = call_args_list[1].args
    assert main_split_call[0] == account
    assert main_split_call[1]["id"] == 2
    assert main_split_call[2]["amount"] == 0

    fx_split_call = call_args_list[2].args
    assert fx_split_call[0] == account
    assert fx_split_call[1]["id"] == 3
    assert fx_split_call[2]["amount"] == 0

