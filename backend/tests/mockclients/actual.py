from backend import Config
from backend.clients.actual import IActualClient


class MockActualClient(IActualClient):
    def create_transaction(self, account_id, transaction):
        pass

    def get_transaction(self, account_id, tx):
        return {
            "id": 1,
            "date": "2024-01-01",
            "amount": -1200,
            "payee_name": "payee",
            "imported_payee": "counterparty",
            "category": Config.actual_other_category,
            "notes": "description",
            "imported_id": "teller_id",
            "cleared": False,
            "subtransactions": [
                {
                    "amount": -1000,
                    "category": Config.actual_other_category,
                    "notes": "Original value in EUR"
                },
                {
                    "amount": -100,
                    "category": Config.actual_fee_category,
                    "notes": "Effective FX fees"
                },
                {
                    "amount": -100,
                    "category": Config.actual_ccy_category,
                    "notes": "Currency Risk"
                }
            ]
        }

    def patch_transaction(self, account_id, actual_tx, updated_fields):
        pass

    def delete_transaction(self, actual_id):
        pass
