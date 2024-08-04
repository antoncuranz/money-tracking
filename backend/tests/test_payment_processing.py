from backend import *
from backend.tests.conftest import with_test_db
from backend.tests.fixtures import *


@with_test_db((Account, Transaction, Exchange, ExchangePayment, Payment, CreditTransaction, ExchangeRate,))
def test_payment_processing(client, payment_service):
    # Arrange
    account = Account.create(**ACCOUNT_1)
    for tx in TRANSACTIONS:
        model = Transaction.create(**tx)
        model.amount_eur = model.amount_usd
        model.save()
    payment = Payment.create(**PAYMENT_1)
    Exchange.create(**EXCHANGE_1)
    ExchangePayment.create(**EXCHANGE_PAYMENT_1)

    # Act
    # create Exchange

    # process Payment
    response = client.post(f"/api/accounts/{account}/payments/{payment}")
    transactions = Transaction.select()

    # Assert
    assert response.status_code == 555
    # assert len(parsed) == 1
    # assert parsed[0]["actual_id"] == ACCOUNT_1["actual_id"]
    # assert parsed[0]["teller_id"] == ACCOUNT_1["teller_id"]
    # assert parsed[0]["name"] == ACCOUNT_1["name"]
    # assert parsed[0]["institution"] == ACCOUNT_1["institution"]
