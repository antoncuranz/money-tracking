from functools import wraps

import pytest
from flask import Flask
from flask_injector import FlaskInjector, singleton
from peewee import SqliteDatabase

from backend import api
from backend.clients.mastercard import IMastercardClient
from backend.clients.teller import ITellerClient
from backend.service.balance_service import BalanceService
from tests.mockclients.mastercard import MockMastercardClient
from tests.mockclients.teller import MockTellerClient


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.register_blueprint(api)

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def with_test_db(dbs: tuple):
    def decorator(func):
        @wraps(func)
        def test_db_closure(*args, **kwargs):
            test_db = SqliteDatabase(":memory:")
            with test_db.bind_ctx(dbs):
                test_db.create_tables(dbs)
                try:
                    func(*args, **kwargs)
                finally:
                    test_db.drop_tables(dbs)
                    test_db.close()

        return test_db_closure

    return decorator


dependencies = []


def configure(binder):
    for dep in dependencies:
        binder.bind(dep["iface"], to=dep["to"], scope=singleton)


@pytest.fixture()
def mastercard_mock(app):
    client = MockMastercardClient()
    dependencies.append({"iface": IMastercardClient, "to": client})
    FlaskInjector(app=app, modules=[configure])

    yield client


@pytest.fixture()
def teller_mock(app):
    client = MockTellerClient()
    dependencies.append({"iface": ITellerClient, "to": client})
    FlaskInjector(app=app, modules=[configure])

    yield client


@pytest.fixture()
def balance_service(app):
    service = BalanceService()
    dependencies.append({"iface": BalanceService, "to": service})
    FlaskInjector(app=app, modules=[configure])

    yield service
