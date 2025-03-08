from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlmodel import SQLModel

import backend.data_export.inbound.api as data_export
import backend.data_import.inbound.api as data_import
import backend.dates.inbound.api as dates
from backend.auth import verify_user_header
from backend.core.inbound import accounts, balances, bank_accounts, credits, exchanges, payments, transactions
from backend.models import engine

app = FastAPI(dependencies=[Depends(verify_user_header)])
for module in [accounts, balances, bank_accounts, credits, dates, exchanges, payments, transactions, data_import, data_export]:
    app.include_router(module.router)


@asynccontextmanager
async def lifespan():
    # on startup
    SQLModel.metadata.create_all(engine)
    yield
    # on shutdown