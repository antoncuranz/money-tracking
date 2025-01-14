from fastapi import FastAPI, Depends

from backend.auth import verify_user_header
from backend.models import ALL_TABLES, db
from backend.core.api import accounts, balances, bank_accounts, credits, dates, exchanges, payments, transactions
import backend.data_import.api as data_import
import backend.data_export.api as data_export

app = FastAPI(dependencies=[Depends(verify_user_header)])
for module in [accounts, balances, bank_accounts, credits, dates, exchanges, payments, transactions, data_import, data_export]:
    app.include_router(module.router)


@app.on_event("startup")
def on_startup():
    db.connect()
    db.create_tables(ALL_TABLES)
