from config import config
from data_export.business.actual_service import ActualService
from models import Transaction
from tests.fixtures import *
import pytest

ACTUAL_TRANSACTION = {
    "id": 1,
    "payee": "payee_1",
    "subtransactions": [
        {"id": 2, "category": None},
        {"id": 3, "category": config.actual_fee_category}
    ]
}

GUESSED_AMOUNT_EUR = 1234


def mock_repository(mocker, get_account_rv):
    repository_mock = mocker.Mock()
    repository_mock.get_account.return_value = get_account_rv
    return repository_mock


def mock_exchangerate(mocker, guess_amount_eur_rv=GUESSED_AMOUNT_EUR):
    exchangerate_mock = mocker.Mock()
    exchangerate_mock.guess_amount_eur.return_value = guess_amount_eur_rv
    return exchangerate_mock


def mock_actual(mocker, get_transaction_rv=ACTUAL_TRANSACTION):
    actual_mock = mocker.Mock()
    actual_mock.get_transaction.return_value = get_transaction_rv
    return actual_mock


@pytest.mark.parametrize("amount_eur,expected_actual_amount", [(1000, -1000), (0, 0), (None, -GUESSED_AMOUNT_EUR)])
def test_update_transaction(mocker, amount_eur, expected_actual_amount):
    # Arrange
    account = mocker.Mock()
    actual_mock = mock_actual(mocker)
    
    tx = Transaction(**TX_1)
    tx.actual_id = "something"
    tx.amount_eur = amount_eur

    under_test = ActualService(actual_mock, mock_exchangerate(mocker), mock_repository(mocker, account))

    # Act
    under_test.update_transaction(session=None, user=None, account_id=1, tx=tx, existing_payees={})
    
    # Assert
    assert actual_mock.patch_transaction.call_count == 3
    call_args_list = actual_mock.patch_transaction.call_args_list
    
    main_tx_call = call_args_list[0].args
    assert main_tx_call[0] == account
    assert main_tx_call[1]["id"] == 1
    assert main_tx_call[2]["cleared"] == (tx.status == 3)
    assert main_tx_call[2]["amount"] == expected_actual_amount
    assert main_tx_call[2]["date"] == str(tx.date)
    assert main_tx_call[2]["imported_payee"] == tx.counterparty
    assert main_tx_call[2]["notes"] == tx.description

    main_split_call = call_args_list[1].args
    assert main_split_call[0] == account
    assert main_split_call[1]["id"] == 2
    assert main_split_call[2]["amount"] == expected_actual_amount
    
    fx_split_call = call_args_list[2].args
    assert fx_split_call[0] == account
    assert fx_split_call[1]["id"] == 3
    assert fx_split_call[2]["amount"] == 0
