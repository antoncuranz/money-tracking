import datetime
from typing import Annotated

from fastapi import Depends

from dates.business.date_service import DateService
from models import Account


class DatesFacade:
    def __init__(self, date_service: Annotated[DateService, Depends()]):
        self.date_service = date_service

    def get_next_due_date(self, account: Account) -> datetime.date:
        return self.date_service.get_next_due_date(account)

    def get_last_due_date(self, account: Account) -> datetime.date:
        return self.date_service.get_last_due_date(account)

    def get_statement_date_for_due_date(self, account: Account, due_date: datetime.date) -> datetime.date:
        return self.date_service.get_statement_date_for_due_date(account, due_date)
