from backend.clients.actual import IActualClient


class MockActualClient(IActualClient):
    def import_transactions(self, account_id, transactions):
        return dict(data=dict(added=["actual_tx_added_1"]))
