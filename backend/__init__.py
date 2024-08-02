from backend.models import *
from flask import Flask
from flask_injector import FlaskInjector, singleton
from backend.clients.actual import ActualClient
from backend.clients.teller import TellerClient
from backend.routes import api
from backend.service.actual_service import ActualService
from backend.service.conversion_service import ConversionService
from backend.service.transaction_service import TransactionService


def configure(binder):
    teller = TellerClient(Config.teller_cert)
    actual = ActualClient(Config.actual_api_key, Config.actual_sync_id)

    binder.bind(TellerClient, to=teller, scope=singleton)
    binder.bind(ActualClient, to=actual, scope=singleton)
    binder.bind(TransactionService, to=TransactionService(teller), scope=singleton)
    binder.bind(ActualService, to=ActualService(actual), scope=singleton)
    binder.bind(ConversionService, to=ConversionService(), scope=singleton)


db.connect()
db.create_tables([Account, Transaction])

app = Flask(__name__)
app.register_blueprint(api)
FlaskInjector(app=app, modules=[configure])

if __name__ == "__main__":
    app.run()
