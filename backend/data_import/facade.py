import datetime
from typing import List, Annotated, Optional

from fastapi import Depends
from sqlmodel import Session

from data_import.dataaccess.dataimport_repository import DataImportRepository


class DataImportFacade:
    def __init__(self, repository: Annotated[DataImportRepository, Depends()]):
        self.repository = repository

    def get_last_successful_update(self, session: Session, plaid_account_id: int) -> Optional[datetime.datetime]:
        return self.repository.get_last_successful_update(session, plaid_account_id)
