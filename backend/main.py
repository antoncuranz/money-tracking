from fastapi import FastAPI, Depends

import backend.data_export.inbound.api as data_export
import backend.data_import.inbound.api as data_import
import backend.dates.inbound.api as dates
from backend.auth import verify_user_header
from backend.core.inbound import accounts, balances, bank_accounts, credits, exchanges, payments, transactions
from backend.models import ALL_TABLES, db

app = FastAPI(dependencies=[Depends(verify_user_header)])
for module in [accounts, balances, bank_accounts, credits, dates, exchanges, payments, transactions, data_import, data_export]:
    app.include_router(module.router)


@app.on_event("startup")
def on_startup():
    db.connect()
    db.create_tables(ALL_TABLES)
