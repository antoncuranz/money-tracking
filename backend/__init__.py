from flask import Flask
from flask_injector import FlaskInjector, singleton

from backend.api.payments import payments
from backend.models import *
from backend.api.api import api
from backend.api.balances import balances
from backend.api.imports import imports
from backend.api.exchanges import exchanges
from backend.api.credits import credits
from backend.api.accounts import accounts
from backend.api.transactions import transactions
from backend.clients.actual import IActualClient, ActualClient
from backend.clients.exchangerates import ExchangeratesApiIoClient, MastercardClient
from backend.clients.teller import TellerClient, ITellerClient
from backend.service.actual_service import ActualService
from backend.service.balance_service import BalanceService
from backend.service.exchange_service import ExchangeService
from backend.service.payment_service import PaymentService
from backend.service.transaction_service import TransactionService


def configure(binder):
    teller = TellerClient(Config.teller_cert)
    actual = ActualClient(Config.actual_api_key, Config.actual_sync_id)
    mastercard = MastercardClient()
    exchangeratesio = ExchangeratesApiIoClient(Config.exchangeratesio_access_key)
    # ibkr = IbkrClient(Config.ibkr_host, Config.ibkr_port)

    binder.bind(ITellerClient, to=teller, scope=singleton)
    binder.bind(IActualClient, to=actual, scope=singleton)
    binder.bind(MastercardClient, to=mastercard, scope=singleton)
    binder.bind(ExchangeratesApiIoClient, to=exchangeratesio, scope=singleton)
    # binder.bind(IbkrClient, to=ibkr, scope=singleton)

    balance_service = BalanceService()
    exchange_service = ExchangeService(mastercard, exchangeratesio)

    binder.bind(TransactionService, to=TransactionService(teller), scope=singleton)
    binder.bind(ActualService, to=ActualService(actual), scope=singleton)
    binder.bind(ExchangeService, to=exchange_service, scope=singleton)
    binder.bind(BalanceService, to=balance_service, scope=singleton)
    binder.bind(PaymentService, to=PaymentService(balance_service, exchange_service, actual), scope=singleton)


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
    app = Flask(__name__)
    register_blueprints(app)
    FlaskInjector(app=app, modules=[configure])

    db.connect()
    db.create_tables([
        Credit, CreditTransaction, Transaction, Exchange, ExchangePayment, Payment, Account, ExchangeRate
    ])

    return app


if __name__ == "__main__":
    create_app().run()
