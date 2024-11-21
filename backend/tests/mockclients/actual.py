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
            "payee": "c5647552-a5b1-4fea-a2bd-4aa2e4d03938",
            "imported_payee": "counterparty",
            "category": None,
            "notes": "description",
            "imported_id": "teller_id",
            "cleared": False,
            "subtransactions": [
                {
                    "amount": -1000,
                    "category": None,
                    "notes": "Original value in EUR"
                },
                {
                    "amount": -200,
                    "category": Config.actual_fee_category,
                    "notes": "FX Fees and CCY Risk"
                }
            ]
        }

    def patch_transaction(self, account_id, actual_tx, updated_fields):
        pass

    def delete_transaction(self, actual_id):
        pass
    
    def get_payees(self):
        return {
          "data": [
            {
              "id": "f733399d-4ccb-4758-b208-7422b27f650a",
              "name": "Fidelity",
              "category": None,
              "transfer_acct": "729cb492-4eab-468b-9522-75d455cded22"
            }
          ]
        }

    def create_payee(self, payee_name):
        return {
            "data": "5b4837d7-f147-4c7c-a315-b21ad484ba4a"
        }
    
    # def get_payee(self, payee_id):
    #     raise NotImplementedError

    # def update_payee(self, payee_id, payee_name):
    #     raise NotImplementedError
