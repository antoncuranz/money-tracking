from flask import Flask
from flask_injector import FlaskInjector, singleton

from backend.models import *
from backend.core.client.exchangerates_client import MastercardClient, ExchangeratesApiIoClient
from backend.data_import.teller_client import TellerClient, ITellerClient
from backend.data_export.actual_client import ActualClient, IActualClient
from backend.core.service.balance_service import BalanceService
from backend.core.service.exchange_service import ExchangeService
from backend.core.service.transaction_service import TransactionService
from backend.data_import.teller_service import TellerService
from backend.data_export.actual_service import ActualService
from backend.core.service.payment_service import PaymentService
from backend.core.api.api import api
from backend.core.api.balances import balances
from backend.core.api.credits import credits
from backend.core.api.accounts import accounts
from backend.data_import.api import imports
from backend.core.api.payments import payments
from backend.core.api.transactions import transactions
from backend.core.api.exchanges import exchanges


def configure(binder):
    teller = TellerClient(Config.teller_cert)
    actual = ActualClient(Config.actual_api_key, Config.actual_base_url)
    mastercard = MastercardClient()
    exchangeratesio = ExchangeratesApiIoClient(Config.exchangeratesio_access_key)

    binder.bind(ITellerClient, to=teller, scope=singleton)
    binder.bind(IActualClient, to=actual, scope=singleton)
    binder.bind(MastercardClient, to=mastercard, scope=singleton)
    binder.bind(ExchangeratesApiIoClient, to=exchangeratesio, scope=singleton)

    balance_service = BalanceService()
    exchange_service = ExchangeService(mastercard, exchangeratesio)
    teller_service = TellerService(teller)
    actual_service = ActualService(actual, exchange_service)

    binder.bind(TellerService, to=teller_service, scope=singleton)
    binder.bind(ActualService, to=actual_service, scope=singleton)
    binder.bind(ExchangeService, to=exchange_service, scope=singleton)
    binder.bind(BalanceService, to=balance_service, scope=singleton)
    binder.bind(TransactionService, to=TransactionService(teller_service, actual_service), scope=singleton)
    binder.bind(PaymentService, to=PaymentService(balance_service, exchange_service, actual_service), scope=singleton)


def register_blueprints(app):
    app.register_blueprint(api)
    app.register_blueprint(accounts)
    app.register_blueprint(transactions)
    app.register_blueprint(payments)
    app.register_blueprint(credits)
    app.register_blueprint(exchanges)
    app.register_blueprint(imports)
    app.register_blueprint(balances)


def create_app():
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))

    app = Flask(__name__)
    register_blueprints(app)
    FlaskInjector(app=app, modules=[configure])

    db.connect()
    db.create_tables([
        Credit, CreditTransaction, Transaction, Exchange, ExchangePayment, Payment, User, Account, ExchangeRate
    ])

    return app


if __name__ == "__main__":
    create_app().run()
