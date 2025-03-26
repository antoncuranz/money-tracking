from time import sleep

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from testcontainers.postgres import PostgresContainer

from core.business.balance_service import BalanceService
from core.dataaccess.account_repository import AccountRepository
from core.dataaccess.credit_repository import CreditRepository
from core.dataaccess.exchange_repository import ExchangeRepository
from core.dataaccess.payment_repository import PaymentRepository
from core.dataaccess.store import Store
from core.dataaccess.transaction_repository import TransactionRepository
from data_export.adapter.actual_client import ActualClient
from data_import.adapter.quiltt_client import QuilttClient
from exchangerate.adapter.exchangerates_client import MastercardClient, ExchangeratesApiIoClient
from models import get_session
from tests.mockclients.actual import MockActualClient
from tests.mockclients.exchangerates import MockExchangeRateClient
from tests.mockclients.quiltt import MockQuilttClient


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
    from main import app

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
    return BalanceService(Store(AccountRepository(), TransactionRepository(), CreditRepository(), PaymentRepository(), ExchangeRepository()), None)