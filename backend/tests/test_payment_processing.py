from backend import *
from backend.tests.conftest import with_test_db
from backend.tests.fixtures import *


@with_test_db((Account, Credit, CreditTransaction, Transaction, Exchange, ExchangePayment, Payment, ExchangeRate))
def test_payment_processing_good_ccy_risk(client, balance_service, payment_service):
    # Arrange
    account = Account.create(**ACCOUNT_1)

    payment, exchange = setup_tables([
        {"date": "2024-01-01", "amount_eur": 1000, "amount_usd": 1015, "rate": 1.01},
        {"date": "2024-01-02", "amount_eur": 10000, "amount_usd": 10250, "rate": 1.02},
        {"date": "2024-01-03", "amount_eur": 2600, "amount_usd": 2691, "rate": 1.03},
        {"date": "2024-01-04", "amount_eur": 4000, "amount_usd": 4180, "rate": 1.04},
        {"date": "2024-01-05", "amount_eur": 8000, "amount_usd": 8440, "rate": 1.05},
    ], exchange_rate=1.1)

    # Act
    response = client.post(f"/api/accounts/{account}/payments/{payment}")

    # Assert (general checks)
    sum_eur = Transaction.select(fn.SUM(Transaction.amount_eur + Transaction.fx_fees + Transaction.ccy_risk)) \
        .where(Transaction.payment == payment).scalar()
    sum_usd = Transaction.select(fn.SUM(Transaction.amount_usd)).where(Transaction.payment == payment).scalar()
    payment = Payment.get()

    assert response.status_code == 555
    assert payment.processed is True
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd
    assert balance_service.calc_exchange_remaining(exchange) == 0

    # Assert (individual values)
    thresh = 2
    tx1 = Transaction.get(Transaction.id == 1)
    assert tx1.fx_fees == 5
    assert tx1.ccy_risk == -82

    tx2 = Transaction.get(Transaction.id == 2)
    assert tx2.fx_fees == 49
    assert tx2.ccy_risk == -731

    tx3 = Transaction.get(Transaction.id == 3)
    assert tx3.fx_fees - 13 < thresh
    assert tx3.ccy_risk == -166

    tx4 = Transaction.get(Transaction.id == 4)
    assert tx4.fx_fees == 19
    assert tx4.ccy_risk == -219

    tx5 = Transaction.get(Transaction.id == 5)
    assert tx5.fx_fees == 38
    assert tx5.ccy_risk == -365


@with_test_db((Account, Credit, CreditTransaction, Transaction, Exchange, ExchangePayment, Payment, ExchangeRate))
def test_payment_processing_bad_ccy_risk(client, balance_service, payment_service):
    # Arrange
    account = Account.create(**ACCOUNT_1)

    payment, exchange = setup_tables([
        {"date": "2024-01-01", "amount_eur":  1000, "amount_usd":  1055, "rate": 1.05},
        {"date": "2024-01-02", "amount_eur": 10000, "amount_usd": 10450, "rate": 1.04},
        {"date": "2024-01-03", "amount_eur":  2600, "amount_usd":  2691, "rate": 1.03},
        {"date": "2024-01-04", "amount_eur":  4000, "amount_usd":  4100, "rate": 1.02},
        {"date": "2024-01-05", "amount_eur":  8000, "amount_usd":  8120, "rate": 1.01},
    ], exchange_rate=1.0)

    # Act
    response = client.post(f"/api/accounts/{account}/payments/{payment}")

    # Assert (general checks)
    sum_eur = Transaction.select(fn.SUM(Transaction.amount_eur + Transaction.fx_fees + Transaction.ccy_risk)) \
        .where(Transaction.payment == payment).scalar()
    sum_usd = Transaction.select(fn.SUM(Transaction.amount_usd)).where(Transaction.payment == payment).scalar()
    payment = Payment.get()

    assert response.status_code == 555
    assert payment.processed is True
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd
    assert balance_service.calc_exchange_remaining(exchange) == 0

    # Assert (individual values)
    tx1 = Transaction.get(Transaction.id == 1)
    assert tx1.fx_fees == 5
    assert tx1.ccy_risk == 50

    tx2 = Transaction.get(Transaction.id == 2)
    assert tx2.fx_fees == 48
    assert tx2.ccy_risk == 402

    tx3 = Transaction.get(Transaction.id == 3)
    assert tx3.fx_fees == 13
    assert tx3.ccy_risk == 78

    tx4 = Transaction.get(Transaction.id == 4)
    assert tx4.fx_fees == 20
    assert tx4.ccy_risk == 80

    tx5 = Transaction.get(Transaction.id == 5)
    assert tx5.fx_fees == 40
    assert tx5.ccy_risk == 80


def setup_tables(transactions, exchange_rate):
    for i, tx in enumerate(transactions):
        Transaction.create(
            account_id=1, teller_id=f"teller_test_tx_{i}", date=tx["date"], counterparty="counterparty", status=2,
            description="description", category="category", amount_usd=tx["amount_usd"], amount_eur=tx["amount_eur"]
        )
        ExchangeRate.create(date=tx["date"], source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=tx["rate"])

    sum_usd = sum(tx["amount_usd"] for tx in transactions)

    exchange = Exchange.create(**EXCHANGE_1)
    exchange.amount_usd = sum_usd
    exchange.exchange_rate = exchange_rate
    exchange.save()

    payment = Payment.create(**PAYMENT_1)
    payment.amount_usd = sum_usd
    payment.save()

    ep = ExchangePayment.create(**EXCHANGE_PAYMENT_1)
    ep.amount = sum_usd
    ep.save()

    return payment, exchange


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
