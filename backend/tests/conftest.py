from time import sleep

import pytest
from flask import Flask
from flask_injector import FlaskInjector, singleton
from testcontainers.postgres import PostgresContainer

from backend import register_blueprints
from backend.models import db, ALL_TABLES, User
from backend.core.client.exchangerates_client import IExchangeRateClient
from backend.core.service.account_service import AccountService
from backend.core.service.balance_service import BalanceService
from backend.core.service.exchange_service import ExchangeService
from backend.core.service.payment_service import PaymentService
from backend.core.service.transaction_service import TransactionService
from backend.core.service.credit_service import CreditService
from backend.data_export.actual_service import ActualService
from backend.data_export.actual_client import IActualClient
from backend.data_import.quiltt_client import IQuilttClient
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


@pytest.fixture(scope="session", autouse=True)
def setup(request):
    postgres = PostgresContainer("postgres:15-alpine").with_bind_ports(5432, 5432)
    postgres.start()

    def remove_container():
        postgres.stop()

    request.addfinalizer(remove_container)
    print("Connecting to test database")
    for i in range(100):
        sleep(0.1)
        try:
            db.create_tables(ALL_TABLES)
            print("Connected to test database (took {} seconds)".format((i+1)/10))
            return
        except Exception:
            pass
    
    raise Exception("Unable to connect to test database")

@pytest.fixture(scope="function", autouse=True)
def setup_data():
    for table in ALL_TABLES:
        table.delete().execute()

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
