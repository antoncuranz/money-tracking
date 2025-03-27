from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Depends
from prometheus_client import make_asgi_app as make_prometheus_app

import data_export.inbound.api as data_export
import dates.inbound.api as dates
from auth import verify_user_header
from core.inbound import user, accounts, balances, bank_accounts, credits, exchanges, payments, transactions
from data_import.inbound import import_routes, plaid_routes
from models import database_url


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_cfg, "head")
    yield
    # on shutdown

app = FastAPI(dependencies=[Depends(verify_user_header)], lifespan=lifespan)
for module in [user, accounts, balances, bank_accounts, credits, dates, exchanges, payments, transactions, import_routes, plaid_routes, data_export]:
    app.include_router(module.router)

app.mount("/metrics", make_prometheus_app())
