from functools import wraps

import pytest
from flask import Flask
from flask_injector import FlaskInjector, singleton
from peewee import SqliteDatabase

from backend import register_blueprints
from backend.clients.actual import IActualClient
from backend.clients.mastercard import IMastercardClient
from backend.clients.teller import ITellerClient
from backend.service.balance_service import BalanceService
from backend.service.exchange_service import ExchangeService
from backend.service.payment_service import PaymentService
from backend.tests.mockclients.actual import MockActualClient
from backend.tests.mockclients.mastercard import MockMastercardClient
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
def mastercard_mock(app):
    client = MockMastercardClient()
    dependencies[IMastercardClient] = client
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
def balance_service(app):
    service = BalanceService()
    dependencies[BalanceService] = service
    FlaskInjector(app=app, modules=[configure])

    yield service


@pytest.fixture()
def exchange_service(app, mastercard_mock):
    service = ExchangeService(mastercard_mock)
    dependencies[ExchangeService] = service
    FlaskInjector(app=app, modules=[configure])

    yield service


@pytest.fixture()
def payment_service(app, balance_service, exchange_service, actual_mock):
    service = PaymentService(balance_service, exchange_service, actual_mock)
    dependencies[PaymentService] = service
    FlaskInjector(app=app, modules=[configure])

    yield service
