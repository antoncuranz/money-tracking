import json
from decimal import Decimal
import pytest
from peewee import DoesNotExist

from backend import Exchange, ExchangePayment, Payment
from backend.tests.conftest import with_test_db
from backend.tests.fixtures import EXCHANGE_1, PAYMENT_1, PAYMENT_2, PAYMENT_3, EXCHANGE_2


@with_test_db((Exchange,))
def test_get_exchanges(client):
    # Arrange
    exchange = Exchange.create(**EXCHANGE_1)

    # Act
    response = client.get("/api/exchanges")
    parsed = json.loads(response.data)

    # Assert
    assert response.status_code == 200
    assert len(parsed) == 1
    assert parsed[0]["id"] == exchange.id


@with_test_db((Exchange,))
def test_post_exchange(client):
    # Arrange

    # Act
    response = client.post("/api/exchanges", json=EXCHANGE_1)

    # Assert
    assert response.status_code == 200
    exchange = Exchange.get()
    assert exchange.amount_usd == EXCHANGE_1["amount_usd"]
    assert exchange.amount_eur == EXCHANGE_1["amount_eur"]
    assert exchange.exchange_rate == Decimal(EXCHANGE_1["exchange_rate"]).quantize(Decimal(10) ** -6)


@with_test_db((Exchange, ExchangePayment))
def test_delete_exchange(client):
    # Arrange
    exchange = Exchange.create(**EXCHANGE_1)

    # Act
    response = client.delete(f"/api/exchanges/{exchange}")

    # Assert
    assert response.status_code == 204
    with pytest.raises(DoesNotExist):
        Exchange.get()


@with_test_db((Exchange, ExchangePayment, Payment))
def test_delete_assigned_exchange_500(client):
    # Arrange
    payment = Payment.create(**PAYMENT_1)
    exchange = Exchange.create(**EXCHANGE_1)
    ExchangePayment.create(exchange=exchange, payment=payment, amount=1)

    # Act
    response = client.delete(f"/api/exchanges/{exchange}")

    # Assert
    assert response.status_code == 500


@with_test_db((Exchange, ExchangePayment, Payment))
def test_update_exchange(app, client, balance_service):
    # Arrange
    exchange = Exchange.create(**EXCHANGE_1)
    payment = Payment.create(**PAYMENT_1)

    assert payment.amount_usd == exchange.amount_usd

    # Act
    response = client.put(f"/api/exchanges/{exchange}?payment={payment}&amount={exchange.amount_usd}")

    # Assert
    assert response.status_code == 204
    assert balance_service.calc_exchange_remaining(exchange) == 0
    assert balance_service.calc_payment_remaining(payment) == 0


@with_test_db((Exchange, ExchangePayment, Payment))
def test_update_exchange_amount_larger_than_payment_500(app, client, balance_service):
    # Arrange
    exchange = Exchange.create(**EXCHANGE_1)
    payment = Payment.create(**PAYMENT_2)

    assert payment.amount_usd < exchange.amount_usd

    # Act
    response = client.put(f"/api/exchanges/{exchange}?payment={payment}&amount={exchange.amount_usd}")

    # Assert
    assert response.status_code == 500


@with_test_db((Exchange, ExchangePayment, Payment))
def test_update_exchange_amount_larger_than_remaining_payment_500(app, client, balance_service):
    # Arrange
    exchange = Exchange.create(**EXCHANGE_1)
    exchange2 = Exchange.create(**EXCHANGE_2)
    payment = Payment.create(**PAYMENT_1)
    ExchangePayment.create(exchange=exchange2, payment=payment, amount=exchange2.amount_usd)

    assert payment.amount_usd == exchange.amount_usd
    assert balance_service.calc_payment_remaining(payment) < exchange.amount_usd

    # Act
    response = client.put(f"/api/exchanges/{exchange}?payment={payment}&amount={exchange.amount_usd}")

    # Assert
    assert response.status_code == 500


@with_test_db((Exchange, ExchangePayment, Payment))
def test_update_exchange_amount_larger_than_exchange_500(app, client, balance_service):
    # Arrange
    exchange = Exchange.create(**EXCHANGE_1)
    payment = Payment.create(**PAYMENT_3)

    assert payment.amount_usd > exchange.amount_usd

    # Act
    response = client.put(f"/api/exchanges/{exchange}?payment={payment}&amount={payment.amount_usd}")

    # Assert
    assert response.status_code == 500


@with_test_db((Exchange, ExchangePayment, Payment))
def test_update_exchange_on_processed_payment_404(app, client, balance_service):
    # Arrange
    exchange = Exchange.create(**EXCHANGE_1)
    payment = Payment.create(**PAYMENT_1)
    payment.processed = True
    payment.save()
    ExchangePayment.create(exchange=exchange, payment=payment, amount=1)

    # Act
    response = client.put(f"/api/exchanges/{exchange}?payment={payment}&amount={exchange.amount_usd}")

    # Assert
    assert response.status_code == 404


@with_test_db((Exchange, ExchangePayment, Payment))
def test_update_exchange_delete_exchange_payment(app, client, balance_service):
    # Arrange
    exchange = Exchange.create(**EXCHANGE_1)
    payment = Payment.create(**PAYMENT_1)
    ExchangePayment.create(exchange=exchange, payment=payment, amount=1)

    # Act
    response = client.put(f"/api/exchanges/{exchange}?payment={payment}&amount={0}")

    # Assert
    assert response.status_code == 204
    with pytest.raises(DoesNotExist):
        ExchangePayment.get()


@with_test_db((Exchange, ExchangePayment, Payment))
def test_update_exchange_reduce_amount(app, client, balance_service):
    # Arrange
    exchange = Exchange.create(**EXCHANGE_1)
    payment = Payment.create(**PAYMENT_1)
    ExchangePayment.create(exchange=exchange, payment=payment, amount=exchange.amount_usd)

    assert payment.amount_usd == exchange.amount_usd

    # Act
    response = client.put(f"/api/exchanges/{exchange}?payment={payment}&amount={exchange.amount_usd-10}")

    # Assert
    assert response.status_code == 204
