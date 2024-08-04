from backend import *
from backend.tests.conftest import with_test_db
from backend.tests.fixtures import *


@with_test_db((Account, Credit, CreditTransaction, Transaction, Exchange, ExchangePayment, Payment, ExchangeRate))
def test_payment_processing(client, payment_service):
    # Arrange
    account = Account.create(**ACCOUNT_1)
    for tx in TRANSACTIONS:
        Transaction.create(**tx)
    payment = Payment.create(**PAYMENT_1)
    Exchange.create(**EXCHANGE_1)
    ExchangePayment.create(**EXCHANGE_PAYMENT_1)
    for er in EXCHANGE_RATES:
        ExchangeRate.create(**er)

    # Act
    response = client.post(f"/api/accounts/{account}/payments/{payment}")

    # Assert
    sum_eur = Transaction.select(fn.SUM(Transaction.amount_eur + Transaction.fx_fees + Transaction.ccy_risk)) \
        .where(Transaction.payment == payment).scalar()
    sum_usd = Transaction.select(fn.SUM(Transaction.amount_usd)).where(Transaction.payment == payment).scalar()
    payment = Payment.get()

    assert response.status_code == 555
    assert payment.processed is True
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd
