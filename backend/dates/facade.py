from typing import Annotated

from fastapi import Depends

from backend.dates.business.date_service import DateServiceDep
from backend.models import Account


class DatesFacade:
    def __init__(self, date_service: DateServiceDep):
        self.date_service = date_service

    def get_next_due_date(self, account: Account):
        self.date_service.get_next_due_date(account)

    def get_statement_date_for_due_date(self, account: Account, due_date):
        self.date_service.get_statement_date_for_due_date(account, due_date)

DatesDep = Annotated[DatesFacade, Depends()]
