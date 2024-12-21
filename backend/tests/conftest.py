from functools import wraps

import pytest
from flask import Flask
from flask_injector import FlaskInjector, singleton
from peewee import SqliteDatabase

from backend import register_blueprints, TransactionService, ActualService, CreditService, IQuilttClient
from backend.core.client.exchangerates_client import IExchangeRateClient
from backend.core.service.account_service import AccountService
from backend.core.service.balance_service import BalanceService
from backend.core.service.exchange_service import ExchangeService
from backend.core.service.payment_service import PaymentService
from backend.data_export.actual_client import IActualClient
from backend.data_import.teller_client import ITellerClient
from backend.data_import.teller_service import TellerService
from backend.tests.mockclients.actual import MockActualClient
from backend.tests.mockclients.exchangerates import MockExchangeRateClient
from backend.tests.mockclients.quiltt import MockQuilttClient
from backend.tests.mockclients.teller import MockTellerClient


@pytest.fixture()
def app():
    app = Flask(__name__)
    register_blueprints(app)

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def with_test_db(dbs: tuple):
    def decorator(func):
        @wraps(func)
        def test_db_closure(*args, **kwargs):
            test_db = SqliteDatabase(":memory:", pragmas=(("foreign_keys", "on"),))
            with test_db.bind_ctx(dbs):
                test_db.create_tables(dbs)
                try:
                    func(*args, **kwargs)
                finally:
                    test_db.drop_tables(dbs)
                    test_db.close()

        return test_db_closure

    return decorator


dependencies = {}


def configure(binder):
    for class_ in dependencies:
        binder.bind(class_, to=dependencies[class_], scope=singleton)


@pytest.fixture()
def exchangerates_mock(app):
    client = MockExchangeRateClient()
    dependencies[IExchangeRateClient] = client
    FlaskInjector(app=app, modules=[configure])

    yield client


@pytest.fixture()
def quiltt_mock(app):
    client = MockQuilttClient()
    dependencies[IQuilttClient] = client
    FlaskInjector(app=app, modules=[configure])

    yield client


@pytest.fixture()
def teller_mock(app):
    client = MockTellerClient()
    dependencies[ITellerClient] = client
    FlaskInjector(app=app, modules=[configure])

    yield client


@pytest.fixture()
def actual_mock(app):
    client = MockActualClient()
    dependencies[IActualClient] = client
    FlaskInjector(app=app, modules=[configure])

    yield client


@pytest.fixture()
def account_service(app):
    service = AccountService()
    dependencies[AccountService] = service
    FlaskInjector(app=app, modules=[configure])

    yield service


@pytest.fixture()
def transaction_service(app, actual_service):
    service = TransactionService(actual_service)
    dependencies[TransactionService] = service
    FlaskInjector(app=app, modules=[configure])

    yield service


@pytest.fixture()
def balance_service(app):
    service = BalanceService()
    dependencies[BalanceService] = service
    FlaskInjector(app=app, modules=[configure])

    yield service


@pytest.fixture()
def credit_service(app, balance_service):
    service = CreditService(balance_service)
    dependencies[CreditService] = service
    FlaskInjector(app=app, modules=[configure])

    yield service


@pytest.fixture()
def exchange_service(app, balance_service, exchangerates_mock):
    service = ExchangeService(balance_service, exchangerates_mock, exchangerates_mock)
    dependencies[ExchangeService] = service
    FlaskInjector(app=app, modules=[configure])

    yield service


@pytest.fixture()
def payment_service(app, balance_service, exchange_service, actual_service):
    service = PaymentService(balance_service, exchange_service, actual_service)
    dependencies[PaymentService] = service
    FlaskInjector(app=app, modules=[configure])

    yield service

@pytest.fixture()
def teller_service(app, teller_mock):
    service = TellerService(teller_mock)
    dependencies[TellerService] = service
    FlaskInjector(app=app, modules=[configure])

    yield service


@pytest.fixture()
def actual_service(app, exchange_service, actual_mock):
    service = ActualService(actual_mock, exchange_service)
    dependencies[ActualService] = service
    FlaskInjector(app=app, modules=[configure])

    yield service
