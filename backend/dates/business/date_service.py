import datetime
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from backend.dates.dataaccess.dates_repository import DatesRepository
from backend.models import Account, User, engine


class DateService:
    def __init__(self, repository: Annotated[DatesRepository, Depends()]):
        self.repository = repository

    def get_dates(self, session: Session, user: User, year: int, month: int):
        selected_month = datetime.date(year, month, 1)

        result = {}
        for account in self.repository.get_accounts_of_user(session, user):
            if account.due_day is None:
                continue

            result[account.id] = dict(color=(account.color if account.color else "black"))
            result[account.id]["statement"] = self.get_statement_date(account, selected_month).isoformat()
            result[account.id]["due"] = self.get_due_date(account, selected_month).isoformat()

        return result

    def get_statement_date(self, account: Account, selected_month: datetime.date) -> datetime.date:
        correct_month = self._get_correct_month(account.due_day, 25, selected_month)
        return correct_month.replace(day=account.due_day) - datetime.timedelta(days=25)

    def get_due_date(self, account: Account, selected_month: datetime.date) -> datetime.date:
        offset = account.autopay_offset if account.autopay_offset else 0
        correct_month = self._get_correct_month(account.due_day, offset, selected_month)
        return correct_month.replace(day=account.due_day) - datetime.timedelta(days=offset)

    def _next_month(self, date: datetime.date) -> datetime.date:
        return (date.replace(day=1) + datetime.timedelta(days=40)).replace(day=1)

    def _previous_month(self, date: datetime.date) -> datetime.date:
        return (date.replace(day=1) - datetime.timedelta(days=10)).replace(day=1)

    def _get_correct_month(self, due_day: int, offset: int, month: datetime.date) -> datetime.date:
        if due_day > offset:
            return month
        else:
            return self._next_month(month)

    def get_next_due_date(self, account: Account) -> datetime.date:
        today = datetime.date.today()
        due_date_current_month = self.get_due_date(account, today)

        if today > due_date_current_month:
            due_date_next_month = self.get_due_date(account, self._next_month(today))
            return due_date_next_month

        return due_date_current_month

    def get_last_due_date(self, account: Account) -> datetime.date:
        today = datetime.date.today()
        due_date_current_month = self.get_due_date(account, today)

        if today <= due_date_current_month:
            due_date_next_month = self.get_due_date(account, self._previous_month(today))
            return due_date_next_month

        return due_date_current_month

    def get_statement_date_for_due_date(self, account: Account, due_date: datetime.date) -> datetime.date:
        offset = account.autopay_offset if account.autopay_offset else 0
        return due_date - datetime.timedelta(days=25-offset)
