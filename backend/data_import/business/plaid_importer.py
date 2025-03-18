import json
import traceback
from decimal import Decimal
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from data_import.business.abstract_importer import AbstractImporter
from data_import.business.plaid_service import PlaidService
from data_import.dataaccess.dataimport_repository import DataImportRepository
from models import Transaction, Account, BankAccount


class PlaidImporter(AbstractImporter):
    def __init__(self, repository: Annotated[DataImportRepository, Depends()],
                 plaid_service: Annotated[PlaidService, Depends()]):
        super().__init__(repository)
        self.plaid_service = plaid_service

    def update_bank_account_balance(self, session: Session, bank_account: BankAccount):
        balance = self.plaid_service.get_account_balance(bank_account.plaid_account)
        bank_account.balance = balance
        session.add(bank_account)
    
    def import_transactions(self, session: Session, account: Account):
        plaid_account = account.plaid_account
        added, _, removed, next_cursor = self.plaid_service.sync_transactions(plaid_account)
        
        for tx in reversed(added):
            if tx["pending"]:
                print("Skipping pending transaction")
                continue
            try:
                if tx["amount"] < 0:
                    payment_strings = ["AUTOPAY PAYMENT", "AUTOPAY PYMT", "MOBILE PAYMENT", "MOBILE PYMT"]
                    if any(payment_string in tx["name"] for payment_string in payment_strings):
                        self._process_payment(session, account, tx)
                    else:
                        self._process_credit(session, account, tx)
                else:
                    self._process_transaction(session, account, tx)
            except:
                print("Error processing plaid transaction: " + self._print_tx(tx))
                traceback.print_exc()
        
        for tx in removed:
            payment = self.repository.get_payment_by_import_id(session, tx["transaction_id"])
            if payment is not None:
                session.delete(payment)
                
            credit = self.repository.get_credit_by_import_id(session, tx["transaction_id"])
            if credit is not None:
                session.delete(credit)
                
            tx = self.repository.get_transaction_by_import_id(session, tx["transaction_id"])
            if tx is not None:
                session.delete(tx)
        
        plaid_account.cursor = next_cursor
        session.add(plaid_account)
        session.commit()
        

    def _make_transaction_args(self, tx, account_id):
        counterparty = next((cp["name"] for cp in tx["counterparties"] if "HIGH" in cp["confidence_level"]), None)
        return {
            "account_id": account_id,
            "import_id": tx["transaction_id"],
            "date": tx["date"],
            "counterparty": counterparty or tx["merchant_name"] or tx["name"],
            "description": tx["name"],
            "amount_usd": abs(int(Decimal(tx["amount"] * 100).quantize(1))),
            "status": Transaction.Status.POSTED.value
        }
