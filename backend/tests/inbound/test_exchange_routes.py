from decimal import Decimal
import pytest
from sqlmodel import Session, select
from fastapi.testclient import TestClient
from sqlalchemy.exc import NoResultFound

from models import Exchange, ExchangePayment, Payment, Account, User, BankAccount
from tests.fixtures import EXCHANGE_1, PAYMENT_1, PAYMENT_2, PAYMENT_3, EXCHANGE_2, ACCOUNT_1, EXCHANGE_1_JSON, \
    ALICE_AUTH, ALICE_USER, BANK_ACCOUNT_1


@pytest.fixture(autouse=True)
def setup(session: Session):
    session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1)])


def test_get_exchanges(session: Session, client: TestClient):
    # Arrange
    exchange = Exchange(**EXCHANGE_1)
    session.add(exchange)
    session.commit()

    # Act
    response = client.get("/api/exchanges", headers=ALICE_AUTH)
    parsed = response.json()

    # Assert
    assert response.status_code == 200
    assert len(parsed) == 1
    assert parsed[0]["id"] == exchange.id


def test_post_exchange(session: Session, client: TestClient):
    # Arrange

    # Act
    response = client.post("/api/exchanges", json=EXCHANGE_1_JSON, headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 200
    exchange = session.exec(select(Exchange)).one()
    assert exchange.amount_usd == EXCHANGE_1["amount_usd"]
    assert exchange.paid_eur == EXCHANGE_1["paid_eur"]
    assert exchange.exchange_rate == Decimal(EXCHANGE_1["exchange_rate"]).quantize(Decimal(10) ** -6)


def test_delete_exchange(session: Session, client: TestClient):
    # Arrange
    exchange = Exchange(**EXCHANGE_1)
    session.add(exchange)
    session.commit()

    # Act
    response = client.delete(f"/api/exchanges/{exchange.id}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 204
    with pytest.raises(NoResultFound):
        session.exec(select(Exchange)).one()


def test_delete_assigned_exchange_500(session: Session, client: TestClient):
    # Arrange
    payment = Payment(**PAYMENT_1)
    session.add(payment)
    exchange = Exchange(**EXCHANGE_1)
    session.add(exchange)
    session.add(ExchangePayment(exchange_id=exchange.id, payment_id=payment.id, amount=1))
    session.commit()

    # Act
    response = client.delete(f"/api/exchanges/{exchange.id}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 500


def test_update_exchange(session: Session, client, balance_service):
    # Arrange
    exchange = Exchange(**EXCHANGE_1)
    session.add(exchange)
    payment = Payment(**PAYMENT_1)
    session.add(payment)
    session.commit()

    assert payment.amount_usd == exchange.amount_usd

    # Act
    response = client.put(f"/api/exchanges/{exchange.id}?payment={payment.id}&amount={exchange.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 204
    assert balance_service.calc_exchange_remaining(session, exchange) == 0
    assert balance_service.calc_payment_remaining(session, payment) == 0


def test_update_exchange_amount_larger_than_payment_500(session: Session, client: TestClient):
    # Arrange
    exchange = Exchange(**EXCHANGE_1)
    session.add(exchange)
    payment = Payment(**PAYMENT_2)
    session.add(payment)
    session.commit()

    assert payment.amount_usd < exchange.amount_usd

    # Act
    response = client.put(f"/api/exchanges/{exchange.id}?payment={payment.id}&amount={exchange.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 500


def test_update_exchange_amount_larger_than_remaining_payment_500(session: Session, client, balance_service):
    # Arrange
    exchange = Exchange(**EXCHANGE_1)
    session.add(exchange)
    exchange2 = Exchange(**EXCHANGE_2)
    session.add(exchange2)
    payment = Payment(**PAYMENT_1)
    session.add(payment)
    session.add(ExchangePayment(exchange_id=exchange2.id, payment_id=payment.id, amount=exchange2.amount_usd))
    session.commit()

    assert payment.amount_usd == exchange.amount_usd
    assert balance_service.calc_payment_remaining(session, payment) < exchange.amount_usd

    # Act
    response = client.put(f"/api/exchanges/{exchange.id}?payment={payment.id}&amount={exchange.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 500


def test_update_exchange_amount_larger_than_exchange_500(session: Session, client: TestClient):
    # Arrange
    exchange = Exchange(**EXCHANGE_1)
    session.add(exchange)
    payment = Payment(**PAYMENT_3)
    session.add(payment)
    session.commit()

    assert payment.amount_usd > exchange.amount_usd

    # Act
    response = client.put(f"/api/exchanges/{exchange.id}?payment={payment.id}&amount={payment.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 500


def test_update_exchange_on_processed_payment_404(session: Session, client: TestClient):
    # Arrange
    exchange = Exchange(**EXCHANGE_1)
    session.add(exchange)
    payment = Payment(**PAYMENT_1)
    payment.status_enum = Payment.Status.PROCESSED
    session.add(payment)
    session.add(ExchangePayment(exchange_id=exchange.id, payment_id=payment.id, amount=1))
    session.commit()

    # Act
    response = client.put(f"/api/exchanges/{exchange.id}?payment={payment.id}&amount={exchange.amount_usd}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 404


def test_update_exchange_delete_exchange_payment(session: Session, client: TestClient):
    # Arrange
    exchange = Exchange(**EXCHANGE_1)
    session.add(exchange)
    payment = Payment(**PAYMENT_1)
    session.add(payment)
    session.add(ExchangePayment(exchange_id=exchange.id, payment_id=payment.id, amount=1))
    session.commit()

    # Act
    response = client.put(f"/api/exchanges/{exchange.id}?payment={payment.id}&amount={0}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 204
    session.exec(select(Exchange)).one()
    session.exec(select(Payment)).one()
    with pytest.raises(NoResultFound):
        session.exec(select(ExchangePayment)).one()


def test_update_exchange_reduce_amount(session: Session, client: TestClient):
    # Arrange
    exchange = Exchange(**EXCHANGE_1)
    session.add(exchange)
    payment = Payment(**PAYMENT_1)
    session.add(payment)
    session.add(ExchangePayment(exchange_id=exchange.id, payment_id=payment.id, amount=exchange.amount_usd))
    session.commit()

    assert payment.amount_usd == exchange.amount_usd

    # Act
    response = client.put(f"/api/exchanges/{exchange.id}?payment={payment.id}&amount={exchange.amount_usd-10}", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 204


def test_get_usable_exchanges(session: Session, client: TestClient):
    # Arrange
    exchange = Exchange(**EXCHANGE_1)
    session.add(exchange)
    payment = Payment(**PAYMENT_1)
    payment.status_enum = Payment.Status.PROCESSED
    session.add(payment)
    session.add(ExchangePayment(exchange_id=exchange.id, payment_id=payment.id, amount=exchange.amount_usd))
    assert payment.amount_usd == exchange.amount_usd

    exchange2 = Exchange(**EXCHANGE_2)
    session.add(exchange2)
    session.commit()

    # Act
    response = client.get(f"/api/exchanges?usable=true", headers=ALICE_AUTH)

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == exchange2.id
