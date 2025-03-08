from models import *
from tests.fixtures import *

from sqlmodel import Session, select, func
from fastapi.testclient import TestClient
import pytest


@pytest.fixture(autouse=True)
def setup(session: Session):
    session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1)])


def test_payment_processing_good_ccy_risk(session: Session, client, balance_service):
    # Arrange
    payment, exchange = _setup_tables(session, [
        {"date": "2024-01-01", "amount_eur":  1000, "amount_usd":  1015, "rate": 1.01},
        {"date": "2024-01-02", "amount_eur": 10000, "amount_usd": 10250, "rate": 1.02},
        {"date": "2024-01-03", "amount_eur":  2600, "amount_usd":  2691, "rate": 1.03},
        {"date": "2024-01-04", "amount_eur":  4000, "amount_usd":  4180, "rate": 1.04},
        {"date": "2024-01-05", "amount_eur":  8000, "amount_usd":  8440, "rate": 1.05},
    ], exchange_rate=1.1)
    session.commit()

    # Act
    response = client.post(f"/api/payments/{payment.id}/process", headers=ALICE_AUTH)

    # Assert (general checks)
    sum_eur, sum_usd, payment = _get_sum_eur_usd_and_payment(session, payment.id)

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd
    assert balance_service.calc_exchange_remaining(session, exchange) == 0

    # Assert (individual values)
    tx1 = session.exec(select(Transaction).where(Transaction.id == 1)).one()
    assert tx1.fees_and_risk_eur == -77

    tx2 = session.exec(select(Transaction).where(Transaction.id == 2)).one()
    assert tx2.fees_and_risk_eur == -682

    tx3 = session.exec(select(Transaction).where(Transaction.id == 3)).one()
    assert tx3.fees_and_risk_eur == -154

    tx4 = session.exec(select(Transaction).where(Transaction.id == 4)).one()
    assert tx4.fees_and_risk_eur == -200

    tx5 = session.exec(select(Transaction).where(Transaction.id == 5)).one()
    assert tx5.fees_and_risk_eur == -327


def test_payment_processing_bad_ccy_risk(session: Session, client, balance_service):
    # Arrange
    payment, exchange = _setup_tables(session, [
        {"date": "2024-01-01", "amount_eur":  1000, "amount_usd":  1055, "rate": 1.05},
        {"date": "2024-01-02", "amount_eur": 10000, "amount_usd": 10450, "rate": 1.04},
        {"date": "2024-01-03", "amount_eur":  2600, "amount_usd":  2691, "rate": 1.03},
        {"date": "2024-01-04", "amount_eur":  4000, "amount_usd":  4100, "rate": 1.02},
        {"date": "2024-01-05", "amount_eur":  8000, "amount_usd":  8120, "rate": 1.01},
    ], exchange_rate=1.0)

    # Act
    response = client.post(f"/api/payments/{payment.id}/process", headers=ALICE_AUTH)

    # Assert (general checks)
    sum_eur, sum_usd, payment = _get_sum_eur_usd_and_payment(session, payment.id)

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd
    assert balance_service.calc_exchange_remaining(session, exchange) == 0

    # Assert (individual values)
    tx1 = session.exec(select(Transaction).where(Transaction.id == 1)).one()
    assert tx1.fees_and_risk_eur == 55

    tx2 = session.exec(select(Transaction).where(Transaction.id == 2)).one()
    assert tx2.fees_and_risk_eur == 450

    tx3 = session.exec(select(Transaction).where(Transaction.id == 3)).one()
    assert tx3.fees_and_risk_eur == 91

    tx4 = session.exec(select(Transaction).where(Transaction.id == 4)).one()
    assert tx4.fees_and_risk_eur == 100

    tx5 = session.exec(select(Transaction).where(Transaction.id == 5)).one()
    assert tx5.fees_and_risk_eur == 120


def test_payment_processing_applied_credit(session: Session, client, balance_service):
    # Arrange
    payment, exchange = _setup_tables(session, [
        {"date": "2024-01-01", "amount_eur":  1000, "amount_usd":  1055, "rate": 1.05},
        {"date": "2024-01-02", "amount_eur": 10000, "amount_usd": 10450, "rate": 1.04},
        {"date": "2024-01-03", "amount_eur":  2600, "amount_usd":  2691, "rate": 1.03},
        {"date": "2024-01-04", "amount_eur":     0, "amount_usd":  4100, "rate": 1.02},
        {"date": "2024-01-05", "amount_eur":  8000, "amount_usd":  8120, "rate": 1.01},
    ], [
        {"date": "2024-01-05", "amount_usd":  4100, "applied_to": 4},
    ], exchange_rate=1.0)

    # Act
    response = client.post(f"/api/payments/{payment.id}/process", headers=ALICE_AUTH)

    # Assert (general checks)
    sum_eur, sum_usd, payment = _get_sum_eur_usd_and_payment(session, payment.id)

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd - 4100 == payment.amount_usd
    assert balance_service.calc_exchange_remaining(session, exchange) == 0

    # Assert (individual values)
    tx1 = session.exec(select(Transaction).where(Transaction.id == 1)).one()
    assert tx1.fees_and_risk_eur == 55

    tx2 = session.exec(select(Transaction).where(Transaction.id == 2)).one()
    assert tx2.fees_and_risk_eur == 450

    tx3 = session.exec(select(Transaction).where(Transaction.id == 3)).one()
    assert tx3.fees_and_risk_eur == 91

    tx4 = session.exec(select(Transaction).where(Transaction.id == 4)).one()
    assert tx4.fees_and_risk_eur == 0

    tx5 = session.exec(select(Transaction).where(Transaction.id == 5)).one()
    assert tx5.fees_and_risk_eur == 120

def test_payment_processing_with_multiple_exchanges(session: Session, client, balance_service):
    # Arrange
    for tx in TRANSACTIONS:
        session.add(Transaction(**tx))
    payment = Payment(**PAYMENT_1)
    session.add(payment)
    ex1 = Exchange(**EXCHANGE_2)
    session.add(ex1)
    ex2 = Exchange(**EXCHANGE_3)
    session.add(ex2)
    session.add(ExchangePayment(**EXCHANGE_PAYMENT_2))
    session.add(ExchangePayment(**EXCHANGE_PAYMENT_3))
    for er in EXCHANGE_RATES:
        session.add(ExchangeRate(**er))

    # Act
    response = client.post(f"/api/payments/{payment.id}/process", headers=ALICE_AUTH)

    # Assert
    sum_eur, sum_usd, payment = _get_sum_eur_usd_and_payment(session, payment.id)

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd
    assert balance_service.calc_exchange_remaining(session, ex1) == 0
    assert balance_service.calc_exchange_remaining(session, ex2) == ex2.amount_usd - (payment.amount_usd - ex1.amount_usd)

def test_payment_processing_with_multiple_exchanges_real_case(session: Session, client: TestClient):
    # Arrange
    session.add(Transaction(
        account_id=1, import_id="import_test_tx_1", date="2024-09-16", counterparty="counterparty1",
        description="description1", category="category", amount_usd=182, amount_eur=164, status=2
    ))
    session.add(Transaction(
        account_id=1, import_id="import_test_tx_2", date="2024-09-16", counterparty="counterparty2",
        description="description2", category="category", amount_usd=666, amount_eur=600, status=2
    ))
    session.add(Transaction(
        account_id=1, import_id="import_test_tx_3", date="2024-09-19", counterparty="counterparty3",
        description="description3", category="category", amount_usd=2996, amount_eur=2677, status=2
    ))
    session.add(Transaction(
        account_id=1, import_id="import_test_tx_4", date="2024-09-19", counterparty="counterparty4",
        description="description4", category="category", amount_usd=500, amount_eur=446, status=2
    ))

    payment = Payment(
        id=1, account_id=1, import_id="import_test_pm_1", date="2024-10-15", counterparty="Capital One", description="Payment",
        category="generic", amount_usd=4344, status=2
    )
    session.add(payment)

    session.add(Exchange(id=1, date="2024-09-17", amount_usd=49789, paid_eur=-1, exchange_rate=Decimal(1.11210)))
    session.add(Exchange(id=2, date="2024-10-16", amount_usd=26378, paid_eur=-1, exchange_rate=Decimal(1.08890)))

    session.add(ExchangePayment(exchange_id=1, payment_id=1, amount=1048))
    session.add(ExchangePayment(exchange_id=2, payment_id=1, amount=3296))

    session.add(ExchangeRate(date="2024-09-16", source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=Decimal(1.11294)))
    session.add(ExchangeRate(date="2024-09-19", source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=Decimal(1.11590)))

    # Act
    response = client.post(f"/api/payments/{payment.id}/process", headers=ALICE_AUTH)

    # Assert
    sum_eur, sum_usd, payment = _get_sum_eur_usd_and_payment(session, payment.id)

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd


def test_payment_processing_with_multiple_exchanges_real_case_2(session: Session, client: TestClient):
    # Arrange
    session.add(Transaction(
        account_id=1, import_id="import_test_tx_1", date="2024-08-10", counterparty="counterparty1",
        description="description1", category="category", amount_usd=861, amount_eur=788, status=2
    ))
    session.add(Transaction(
        account_id=1, import_id="import_test_tx_2", date="2024-08-12", counterparty="counterparty2",
        description="description2", category="category", amount_usd=864, amount_eur=790, status=2
    ))
    session.add(Transaction(
        account_id=1, import_id="import_test_tx_3", date="2024-08-20", counterparty="counterparty3",
        description="description3", category="category", amount_usd=880, amount_eur=795, status=2
    ))

    payment = Payment(
        id=1, account_id=1, import_id="import_test_pm_1", date="2024-09-15", counterparty="Capital One", description="Payment",
        category="generic", amount_usd=2605, status=2
    )
    session.add(payment)

    session.add(Exchange(id=1, date="2024-08-06", amount_usd=27995, paid_eur=-1, exchange_rate=Decimal(1.09219)))
    session.add(Exchange(id=2, date="2024-09-17", amount_usd=49789, paid_eur=-1, exchange_rate=Decimal(1.11210)))

    session.add(ExchangePayment(exchange_id=1, payment_id=1, amount=1903))
    session.add(ExchangePayment(exchange_id=2, payment_id=1, amount=702))

    session.add(ExchangeRate(date="2024-08-10", source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=Decimal(1.09224)))
    session.add(ExchangeRate(date="2024-08-12", source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=Decimal(1.09360)))
    session.add(ExchangeRate(date="2024-08-20", source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=Decimal(1.11276)))

    # Act
    response = client.post(f"/api/payments/{payment.id}/process", headers=ALICE_AUTH)

    # Assert
    sum_eur, sum_usd, payment = _get_sum_eur_usd_and_payment(session, payment.id)

    assert response.status_code == 204
    assert payment.status_enum == Payment.Status.PROCESSED
    assert sum_eur == payment.amount_eur
    assert sum_usd == payment.amount_usd


def _setup_tables(session: Session, transactions, credits=[], exchange_rate=1.0):
    for i, tx in enumerate(transactions):
        session.add(Transaction(
            id=i+1, account_id=1, import_id=f"import_test_tx_{i}", date=tx["date"], counterparty="counterparty", status=2,
            description="description", category="category", amount_usd=tx["amount_usd"], amount_eur=tx["amount_eur"]
        ))
        session.add(ExchangeRate(date=tx["date"], source=ExchangeRate.Source.EXCHANGERATESIO.value, exchange_rate=tx["rate"]))

    for i, credit in enumerate(credits):
        model = Credit(
            id=i+1, account_id=1, import_id=f"import_test_credit_{i}", date=credit["date"], counterparty="counterparty",
            description="description", category="category", amount_usd=credit["amount_usd"]
        )
        session.add(model)
        session.add(CreditTransaction(credit_id=model.id, transaction_id=credit["applied_to"], amount=credit["amount_usd"]))

    sum_usd = sum(tx["amount_usd"] for tx in transactions) - sum(credit["amount_usd"] for credit in credits)

    exchange = Exchange(**EXCHANGE_1)

    exchange.amount_usd = sum_usd
    exchange.exchange_rate = Decimal(exchange_rate)
    session.add(exchange)

    payment = Payment(**PAYMENT_1)

    payment.amount_usd = sum_usd
    session.add(payment)

    ep = ExchangePayment(**EXCHANGE_PAYMENT_1)

    ep.amount = sum_usd
    session.add(ep)

    return payment, exchange


def _get_sum_eur_usd_and_payment(session: Session, payment_id: int):
    sum_eur = session.exec(
        select(func.sum(Transaction.amount_eur + Transaction.fees_and_risk_eur))
        .where(Transaction.payment_id == payment_id)
    ).one()
    sum_usd = session.exec(select(func.sum(Transaction.amount_usd)).where(Transaction.payment_id == payment_id)).one()
    payment = session.exec(select(Payment)).one()
    
    return sum_eur, sum_usd, payment
