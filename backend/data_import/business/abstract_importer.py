import abc
from typing import Annotated

import requests
from fastapi import Depends
from sqlmodel import Session
from abc import ABC

from config import config
from data_import.dataaccess.dataimport_repository import DataImportRepository
from models import Account


class AbstractImporter(ABC):
    def __init__(self, repository: Annotated[DataImportRepository, Depends()]):
        self.repository = repository

    @abc.abstractmethod
    def update_bank_account_balance(self, session: Session, bank_account):
        pass

    @abc.abstractmethod
    def import_transactions(self, session: Session, account: Account):
        pass
    
    @abc.abstractmethod
    def _make_transaction_args(self, tx, account_id):
        pass

    def _process_payment(self, session: Session, account: Account, tx):
        args = self._make_transaction_args(tx, account.id)
        
        pending_payment = self.repository.get_pending_payment(session, account.id, args["date"], args["amount_usd"])
        if pending_payment:
            print("Matching payment " + str(pending_payment.id))
            pending_payment = pending_payment.model_copy(update=args)
            session.add(pending_payment)
            session.commit()
            return

        args = self._make_transaction_args(tx, account.id)
        result, created = self.repository.get_or_create_payment(session, args["import_id"], args)

        if created:
            self._send_notification("A Payment could not be matched")
            print("Error: Could not find pending Payment for {}.".format(self._print_tx(tx)))
            session.commit()
    
    def _print_tx(self, plaid_tx):
        return "(id: {}; date: {}; name: {}; amount: {})".format(
            plaid_tx["transaction_id"], plaid_tx["date"], plaid_tx["name"], plaid_tx["amount"]
        )
            
    def _process_transaction(self, session: Session, account: Account, tx):
        args = self._make_transaction_args(tx, account.id)
        self.repository.get_or_create_transaction(session, args["import_id"], args)

    def _process_credit(self, session: Session, account: Account, tx):
        args = self._make_transaction_args(tx, account.id)
        self.repository.get_or_create_credit(session, args["import_id"], args)

    # TODO: move somewhere else!
    def _send_notification(self, msg, priority=0):
        requests.post("https://api.pushover.net/1/messages.json", data = {
            "token": config.pushover_token,
            "user": config.pushover_user,
            "message": msg,
            "priority": priority
        })
