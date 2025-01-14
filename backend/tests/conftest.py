from time import sleep

import pytest
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from backend.core.business.balance_service import BalanceService
from backend.data_export.adapter.actual_client import ActualClient
from backend.data_import.adapter.quiltt_client import QuilttClient
from backend.data_import.adapter.teller_client import TellerClient
from backend.exchangerate.adapter.exchangerates_client import MastercardClient, ExchangeratesApiIoClient
from backend.models import db, ALL_TABLES
from backend.tests.mockclients.actual import MockActualClient
from backend.tests.mockclients.exchangerates import MockExchangeRateClient
from backend.tests.mockclients.quiltt import MockQuilttClient
from backend.tests.mockclients.teller import MockTellerClient


@pytest.fixture()
def client():
    from backend.main import app
    app.dependency_overrides = {
        ActualClient: MockActualClient,
        MastercardClient: MockExchangeRateClient,
        ExchangeratesApiIoClient: MockExchangeRateClient,
        TellerClient: MockTellerClient,
        QuilttClient: MockQuilttClient
    }
    return TestClient(app)


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

@pytest.fixture()
def balance_service():
    return BalanceService()