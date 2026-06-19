from time import sleep

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
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
from statement_match.adapter.llm_client import StatementMatchLlmClient
from statement_match.adapter.pdf_extractor import PdfExtractor
from tests.mockclients.quiltt import MockQuilttClient
from tests.mockclients.statement_match import MockPdfExtractor, MockStatementMatchLlmClient


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


@pytest.fixture(scope="session")
def sqlite_engine():
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

@pytest.fixture(name="session")  
def session_fixture(engine):
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session


@pytest.fixture(name="sqlite_session")
def sqlite_session_fixture(sqlite_engine):
    SQLModel.metadata.drop_all(sqlite_engine)
    SQLModel.metadata.create_all(sqlite_engine)

    with Session(sqlite_engine) as session:
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


@pytest.fixture(name="sqlite_client")
def sqlite_client_fixture(sqlite_session: Session):
    from main import app

    def get_session_override():
        return sqlite_session

    app.dependency_overrides = {
        get_session: get_session_override,
        ActualClient: MockActualClient,
        MastercardClient: MockExchangeRateClient,
        ExchangeratesApiIoClient: MockExchangeRateClient,
        QuilttClient: MockQuilttClient,
    }

    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


@pytest.fixture()
def balance_service():
    return BalanceService(Store(AccountRepository(), TransactionRepository(), CreditRepository(), PaymentRepository(), ExchangeRepository()), None, None)


@pytest.fixture(autouse=True)
def reset_mock_clients():
    MockActualClient.reset()
    MockPdfExtractor.reset()
    MockStatementMatchLlmClient.reset()
    yield
    MockActualClient.reset()
    MockPdfExtractor.reset()
    MockStatementMatchLlmClient.reset()


@pytest.fixture()
def override_statement_match_dependencies(client: TestClient):
    from main import app

    app.dependency_overrides[PdfExtractor] = MockPdfExtractor
    app.dependency_overrides[StatementMatchLlmClient] = MockStatementMatchLlmClient
    yield MockPdfExtractor, MockStatementMatchLlmClient
    app.dependency_overrides.pop(PdfExtractor, None)
    app.dependency_overrides.pop(StatementMatchLlmClient, None)
