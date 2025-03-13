from typing import Optional, List

from data_export.adapter import openapi
from data_export.adapter.actual_client import IActualClient
from models import config, Account, Transaction, User


class MockActualClient(IActualClient):
    def create_transaction(self, account: Account, transaction: openapi.Transaction):
        pass
    
    def create_transaction_super_misc(self, super_user: User, transaction: openapi.Transaction):
        pass

    def get_transaction(self, account: Account, tx: Transaction) -> Optional[openapi.Transaction]:
        return openapi.Transaction(
            id="1",
            date="2024-01-01",
            amount=-1200,
            payee="c5647552-a5b1-4fea-a2bd-4aa2e4d03938",
            imported_payee="counterparty",
            category=None,
            notes="description",
            imported_id="teller_id",
            cleared=False,
            subtransactions=[
                openapi.Transaction(
                    amount=-1000,
                    category=None,
                    notes="Original value in EUR"
                ),
                openapi.Transaction(
                    amount=-200,
                    category=config.actual_fee_category,
                    notes="FX Fees and CCY Risk"
                )
            ]
        )

    def patch_transaction(self, account: Account, actual_tx: openapi.Transaction, updated_fields):
        pass

    def delete_transaction(self, user: User, actual_id: str):
        pass

    def get_payees(self, user: User) -> List[openapi.Payee]:
        return [
            openapi.Payee(
              id="f733399d-4ccb-4758-b208-7422b27f650a",
              name="Fidelity",
              category=None,
              transfer_acct="729cb492-4eab-468b-9522-75d455cded22"
            )
        ]

    def create_payee(self, user: User, payee_name: str) -> str:
        return "5b4837d7-f147-4c7c-a315-b21ad484ba4a"
