from backend.models import *
from backend.tests.fixtures import *


def test_payment_processing_good_ccy_risk(client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)

    payment, exchange = setup_tables([
        {"date": "2024-01-01", "amount_eur":  1000, "amount_usd":  1015, "rate": 1.01},
        {"date": "2024-01-02", "amount_eur": 10000, "amount_usd": 10250, "rate": 1.02},
        {"date": "2024-01-03", "amount_eur":  2600, "amount_usd":  2691, "rate": 1.03},
        {"date": "2024-01-04", "amount_eur":  4000, "amount_usd":  4180, "rate": 1.04},
        {"date": "2024-01-05", "amount_eur":  8000, "amount_usd":  8440, "rate": 1.05},
    ], exchange_rate=1.1)

    # Act
    response = client.post(f"/api/payments/{payment}/process", headers=ALICE_AUTH)

    # Assert (general checks)
    sum_eur = Transaction.select(fn.SUM(Transaction.amount_eur + Transaction.fees_and_risk_eur)) \
        .where(Transaction.payment == payment).scalar()
    sum_usd = Transaction.select(fn.SUM(Transaction.amount_usd)).where(Transaction.payment == payment).scalar()
    payment = Payment.get()

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd
    assert balance_service.calc_exchange_remaining(exchange) == 0

    # Assert (individual values)
    tx1 = Transaction.get(Transaction.id == 1)
    assert tx1.fees_and_risk_eur == -77

    tx2 = Transaction.get(Transaction.id == 2)
    assert tx2.fees_and_risk_eur == -682

    tx3 = Transaction.get(Transaction.id == 3)
    assert tx3.fees_and_risk_eur == -154

    tx4 = Transaction.get(Transaction.id == 4)
    assert tx4.fees_and_risk_eur == -200

    tx5 = Transaction.get(Transaction.id == 5)
    assert tx5.fees_and_risk_eur == -327


def test_payment_processing_bad_ccy_risk(client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)

    payment, exchange = setup_tables([
        {"date": "2024-01-01", "amount_eur":  1000, "amount_usd":  1055, "rate": 1.05},
        {"date": "2024-01-02", "amount_eur": 10000, "amount_usd": 10450, "rate": 1.04},
        {"date": "2024-01-03", "amount_eur":  2600, "amount_usd":  2691, "rate": 1.03},
        {"date": "2024-01-04", "amount_eur":  4000, "amount_usd":  4100, "rate": 1.02},
        {"date": "2024-01-05", "amount_eur":  8000, "amount_usd":  8120, "rate": 1.01},
    ], exchange_rate=1.0)

    # Act
    response = client.post(f"/api/payments/{payment}/process", headers=ALICE_AUTH)

    # Assert (general checks)
    sum_eur = Transaction.select(fn.SUM(Transaction.amount_eur + Transaction.fees_and_risk_eur)) \
        .where(Transaction.payment == payment).scalar()
    sum_usd = Transaction.select(fn.SUM(Transaction.amount_usd)).where(Transaction.payment == payment).scalar()
    payment = Payment.get()

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd
    assert balance_service.calc_exchange_remaining(exchange) == 0

    # Assert (individual values)
    tx1 = Transaction.get(Transaction.id == 1)
    assert tx1.fees_and_risk_eur == 55

    tx2 = Transaction.get(Transaction.id == 2)
    assert tx2.fees_and_risk_eur == 450

    tx3 = Transaction.get(Transaction.id == 3)
    assert tx3.fees_and_risk_eur == 91

    tx4 = Transaction.get(Transaction.id == 4)
    assert tx4.fees_and_risk_eur == 100

    tx5 = Transaction.get(Transaction.id == 5)
    assert tx5.fees_and_risk_eur == 120


def test_payment_processing_applied_credit(client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)

    payment, exchange = setup_tables([
        {"date": "2024-01-01", "amount_eur":  1000, "amount_usd":  1055, "rate": 1.05},
        {"date": "2024-01-02", "amount_eur": 10000, "amount_usd": 10450, "rate": 1.04},
        {"date": "2024-01-03", "amount_eur":  2600, "amount_usd":  2691, "rate": 1.03},
        {"date": "2024-01-04", "amount_eur":     0, "amount_usd":  4100, "rate": 1.02},
        {"date": "2024-01-05", "amount_eur":  8000, "amount_usd":  8120, "rate": 1.01},
    ], [
        {"date": "2024-01-05", "amount_usd":  4100, "applied_to": 4},
    ], exchange_rate=1.0)

    # Act
    response = client.post(f"/api/payments/{payment}/process", headers=ALICE_AUTH)

    # Assert (general checks)
    sum_eur = Transaction.select(fn.SUM(Transaction.amount_eur + Transaction.fees_and_risk_eur)) \
        .where(Transaction.payment == payment).scalar()
    sum_usd = Transaction.select(fn.SUM(Transaction.amount_usd)).where(Transaction.payment == payment).scalar()
    payment = Payment.get()

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd - 4100 == payment.amount_usd
    assert balance_service.calc_exchange_remaining(exchange) == 0

    # Assert (individual values)
    tx1 = Transaction.get(Transaction.id == 1)
    assert tx1.fees_and_risk_eur == 55

    tx2 = Transaction.get(Transaction.id == 2)
    assert tx2.fees_and_risk_eur == 450

    tx3 = Transaction.get(Transaction.id == 3)
    assert tx3.fees_and_risk_eur == 91

    tx4 = Transaction.get(Transaction.id == 4)
    assert tx4.fees_and_risk_eur == 0

    tx5 = Transaction.get(Transaction.id == 5)
    assert tx5.fees_and_risk_eur == 120


def setup_tables(transactions, credits=[], exchange_rate=1.0):
    for i, tx in enumerate(transactions):
        Transaction.create(
            id=i+1, account_id=1, import_id=f"import_test_tx_{i}", date=tx["date"], counterparty="counterparty", status=2,
            description="description", category="category", amount_usd=tx["amount_usd"], amount_eur=tx["amount_eur"]
        )
        ExchangeRate.create(date=tx["date"], source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=tx["rate"])

    for i, credit in enumerate(credits):
        model = Credit.create(
            id=i+1, account_id=1, import_id=f"import_test_credit_{i}", date=credit["date"], counterparty="counterparty",
            description="description", category="category", amount_usd=credit["amount_usd"]
        )
        CreditTransaction.create(credit=model, transaction_id=credit["applied_to"], amount=credit["amount_usd"])

    sum_usd = sum(tx["amount_usd"] for tx in transactions) - sum(credit["amount_usd"] for credit in credits)

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


def test_payment_processing_with_multiple_exchanges(client, balance_service):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)
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
    response = client.post(f"/api/payments/{payment}/process", headers=ALICE_AUTH)

    # Assert
    sum_eur = Transaction.select(fn.SUM(Transaction.amount_eur + Transaction.fees_and_risk_eur)) \
        .where(Transaction.payment == payment).scalar()
    sum_usd = Transaction.select(fn.SUM(Transaction.amount_usd)).where(Transaction.payment == payment).scalar()
    payment = Payment.get()

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd
    assert balance_service.calc_exchange_remaining(ex1) == 0
    assert balance_service.calc_exchange_remaining(ex2) == ex2.amount_usd - (payment.amount_usd - ex1.amount_usd)

def test_payment_processing_with_multiple_exchanges_real_case(client):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)

    Transaction.create(
        account_id=1, import_id="import_test_tx_1", date="2024-09-16", counterparty="counterparty1",
        description="description1", category="category", amount_usd=182, amount_eur=164, status=2
    )
    Transaction.create(
        account_id=1, import_id="import_test_tx_2", date="2024-09-16", counterparty="counterparty2",
        description="description2", category="category", amount_usd=666, amount_eur=600, status=2
    )
    Transaction.create(
        account_id=1, import_id="import_test_tx_3", date="2024-09-19", counterparty="counterparty3",
        description="description3", category="category", amount_usd=2996, amount_eur=2677, status=2
    )
    Transaction.create(
        account_id=1, import_id="import_test_tx_4", date="2024-09-19", counterparty="counterparty4",
        description="description4", category="category", amount_usd=500, amount_eur=446, status=2
    )

    payment = Payment.create(
        id=1, account_id=1, import_id="import_test_pm_1", date="2024-10-15", counterparty="Capital One", description="Payment",
        category="generic", amount_usd=4344, status=2
    )

    Exchange.create(id=1, date="2024-09-17", amount_usd=49789, paid_eur=-1, exchange_rate=1.11210)
    Exchange.create(id=2, date="2024-10-16", amount_usd=26378, paid_eur=-1, exchange_rate=1.08890)

    ExchangePayment.create(exchange_id=1, payment_id=1, amount=1048)
    ExchangePayment.create(exchange_id=2, payment_id=1, amount=3296)

    ExchangeRate.create(date="2024-09-16", source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=1.11294)
    ExchangeRate.create(date="2024-09-19", source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=1.11590)

    # Act
    response = client.post(f"/api/payments/{payment}/process", headers=ALICE_AUTH)

    # Assert
    sum_eur = Transaction.select(fn.SUM(Transaction.amount_eur + Transaction.fees_and_risk_eur)) \
        .where(Transaction.payment == payment).scalar()
    sum_usd = Transaction.select(fn.SUM(Transaction.amount_usd)).where(Transaction.payment == payment).scalar()
    payment = Payment.get()

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd


def test_payment_processing_with_multiple_exchanges_real_case_2(client):
    # Arrange
    User.create(**ALICE_USER)
    Account.create(**ACCOUNT_1)

    Transaction.create(
        account_id=1, import_id="import_test_tx_1", date="2024-08-10", counterparty="counterparty1",
        description="description1", category="category", amount_usd=861, amount_eur=788, status=2
    )
    Transaction.create(
        account_id=1, import_id="import_test_tx_2", date="2024-08-12", counterparty="counterparty2",
        description="description2", category="category", amount_usd=864, amount_eur=790, status=2
    )
    Transaction.create(
        account_id=1, import_id="import_test_tx_3", date="2024-08-20", counterparty="counterparty3",
        description="description3", category="category", amount_usd=880, amount_eur=795, status=2
    )

    payment = Payment.create(
        id=1, account_id=1, import_id="import_test_pm_1", date="2024-09-15", counterparty="Capital One", description="Payment",
        category="generic", amount_usd=2605, status=2
    )

    Exchange.create(id=1, date="2024-08-06", amount_usd=27995, paid_eur=-1, exchange_rate=1.09219)
    Exchange.create(id=2, date="2024-09-17", amount_usd=49789, paid_eur=-1, exchange_rate=1.11210)

    ExchangePayment.create(exchange_id=1, payment_id=1, amount=1903)
    ExchangePayment.create(exchange_id=2, payment_id=1, amount=702)

    ExchangeRate.create(date="2024-08-10", source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=1.09224)
    ExchangeRate.create(date="2024-08-12", source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=1.09360)
    ExchangeRate.create(date="2024-08-20", source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=1.11276)

    # Act
    response = client.post(f"/api/payments/{payment}/process", headers=ALICE_AUTH)

    # Assert
    sum_eur = Transaction.select(fn.SUM(Transaction.amount_eur + Transaction.fees_and_risk_eur)) \
        .where(Transaction.payment == payment).scalar()
    sum_usd = Transaction.select(fn.SUM(Transaction.amount_usd)).where(Transaction.payment == payment).scalar()
    payment = Payment.get()

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd
