import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from models import Account, BankAccount, Transaction, User
from tests.fixtures import ACCOUNT_1, ALICE_AUTH, ALICE_USER, BANK_ACCOUNT_1
from tests.mockclients.actual import MockActualClient


def test_export_transactions_persists_actual_id_before_update(sqlite_engine, sqlite_session: Session, sqlite_client: TestClient):
    sqlite_session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1)])
    sqlite_session.add(Transaction(
        id=1,
        account_id=1,
        import_id="import_test_tx_1",
        date=datetime.date(2024, 1, 1),
        counterparty="counterparty",
        description="description",
        category="category",
        amount_usd=1015,
        amount_eur=1000,
        status=Transaction.Status.POSTED.value,
    ))
    sqlite_session.commit()

    MockActualClient.fail_on_patch_call = 1

    response = sqlite_client.post("/api/export/actual/1", headers=ALICE_AUTH)

    assert response.status_code == 500
    assert len(MockActualClient.created_transactions) == 1

    with Session(sqlite_engine) as session:
        tx = session.exec(select(Transaction).where(Transaction.id == 1)).one()
        assert tx.actual_id == MockActualClient.created_transactions[0].id


def test_export_transactions_persists_earlier_actual_ids_when_later_export_fails(
    sqlite_engine, sqlite_session: Session, sqlite_client: TestClient
):
    sqlite_session.add_all([User(**ALICE_USER), BankAccount(**BANK_ACCOUNT_1), Account(**ACCOUNT_1)])
    sqlite_session.add(Transaction(
        id=1,
        account_id=1,
        import_id="import_test_tx_1",
        date=datetime.date(2024, 1, 1),
        counterparty="counterparty-1",
        description="description-1",
        category="category",
        amount_usd=1015,
        amount_eur=1000,
        status=Transaction.Status.POSTED.value,
    ))
    sqlite_session.add(Transaction(
        id=2,
        account_id=1,
        import_id="import_test_tx_2",
        date=datetime.date(2024, 1, 2),
        counterparty="counterparty-2",
        description="description-2",
        category="category",
        amount_usd=2020,
        amount_eur=2000,
        status=Transaction.Status.POSTED.value,
    ))
    sqlite_session.commit()

    MockActualClient.fail_on_transaction_create_call = 2

    response = sqlite_client.post("/api/export/actual/1", headers=ALICE_AUTH)

    assert response.status_code == 500
    assert len(MockActualClient.created_transactions) == 2

    sqlite_session.rollback()

    with Session(sqlite_engine) as session:
        tx1 = session.exec(select(Transaction).where(Transaction.id == 1)).one()
        tx2 = session.exec(select(Transaction).where(Transaction.id == 2)).one()

        assert tx1.actual_id == MockActualClient.created_transactions[0].id
        assert tx2.actual_id is None
