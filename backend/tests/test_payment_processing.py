from backend import *
from backend.tests.conftest import with_test_db
from backend.tests.fixtures import *


@with_test_db((Account, Credit, CreditTransaction, Transaction, Exchange, ExchangePayment, Payment, ExchangeRate))
def test_payment_processing(client, balance_service, payment_service):
    # Arrange
    account = Account.create(**ACCOUNT_1)
    for tx in TRANSACTIONS:
        Transaction.create(**tx)
    payment = Payment.create(**PAYMENT_1)
    ex = Exchange.create(**EXCHANGE_1)
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
    assert balance_service.calc_exchange_remaining(ex) == 0


@with_test_db((Account, Credit, CreditTransaction, Transaction, Exchange, ExchangePayment, Payment, ExchangeRate))
def test_payment_processing_with_multiple_exchanges(client, balance_service, payment_service):
    # Arrange
    account = Account.create(**ACCOUNT_1)
    for tx in TRANSACTIONS:
        Transaction.create(**tx)
    payment = Payment.create(**PAYMENT_1)
    ex1 = Exchange.create(**EXCHANGE_2)
    ex2 = Exchange.create(**EXCHANGE_3)
    ExchangePayment.create(**EXCHANGE_PAYMENT_2)
    ExchangePayment.create(**EXCHANGE_PAYMENT_3)
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
    assert balance_service.calc_exchange_remaining(ex1) == 0
    assert balance_service.calc_exchange_remaining(ex2) == ex2.amount_usd - (payment.amount_usd - ex1.amount_usd)
