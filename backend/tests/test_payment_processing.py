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
    sum_eur = Transaction.select(fn.SUM(Transaction.amount_eur + Transaction.fx_fees + Transaction.ccy_risk)).where(
        Transaction.payment == payment).scalar()
    sum_usd = Transaction.select(fn.SUM(Transaction.amount_eur)).where(Transaction.payment == payment).scalar()
    payment = Payment.get()

    # Assert
    assert response.status_code == 555
    assert payment.processed is True
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd
    # assert len(parsed) == 1
    # assert parsed[0]["actual_id"] == ACCOUNT_1["actual_id"]
    # assert parsed[0]["teller_id"] == ACCOUNT_1["teller_id"]
    # assert parsed[0]["name"] == ACCOUNT_1["name"]
    # assert parsed[0]["institution"] == ACCOUNT_1["institution"]
