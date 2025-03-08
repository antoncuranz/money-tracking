from time import sleep

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from testcontainers.postgres import PostgresContainer

from backend.core.business.balance_service import BalanceService
from backend.core.dataaccess.account_repository import AccountRepository
from backend.core.dataaccess.credit_repository import CreditRepository
from backend.core.dataaccess.exchange_repository import ExchangeRepository
from backend.core.dataaccess.payment_repository import PaymentRepository
from backend.core.dataaccess.store import Store
from backend.core.dataaccess.transaction_repository import TransactionRepository
from backend.data_export.adapter.actual_client import ActualClient
from backend.data_import.adapter.quiltt_client import QuilttClient
from backend.exchangerate.adapter.exchangerates_client import MastercardClient, ExchangeratesApiIoClient
from backend.models import get_session
from backend.tests.mockclients.actual import MockActualClient
from backend.tests.mockclients.exchangerates import MockExchangeRateClient
from backend.tests.mockclients.quiltt import MockQuilttClient


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15-alpine").with_bind_ports(5432, 5434) as postgres:
        yield postgres

@pytest.fixture(scope="session", name="engine")
def engine_fixture(postgres_container: PostgresContainer):
    engine = create_engine(postgres_container.get_connection_url())
    
    for i in range(100):
        try:
            SQLModel.metadata.create_all(engine)
            print("Connected to test database (took {} seconds)".format((i+1)/10))
            break
        except Exception:
            sleep(0.1)
            pass
    
    yield engine

@pytest.fixture(name="session")  
def session_fixture(engine):
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    from backend.main import app

    def get_session_override():
        return session

    app.dependency_overrides = {
        get_session: get_session_override,
        ActualClient: MockActualClient,
        MastercardClient: MockExchangeRateClient,
        ExchangeratesApiIoClient: MockExchangeRateClient,
        QuilttClient: MockQuilttClient
    }

    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def balance_service():
    return BalanceService(Store(AccountRepository(), TransactionRepository(), CreditRepository(), PaymentRepository(), ExchangeRepository()))