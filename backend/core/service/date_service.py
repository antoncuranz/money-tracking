import datetime

from flask_injector import inject

from backend.models import Account


class DateService:
    @inject
    def __init__(self):
        pass
        
    def get_dates(self, year, month):
        selected_month = datetime.date(int(year), int(month), 1)

        result = {}
        for account in Account.select().where(Account.user == g.user.id):
            if account.due_day is None:
                continue
            result[account.id] = dict(color=(account.color if account.color else "black"))

            correct_month = self._get_correct_month(account.due_day, 25, selected_month)
            result[account.id]["statement"] = (
                    correct_month.replace(day=account.due_day) - datetime.timedelta(days=25)).isoformat()

            offset = account.autopay_offset if account.autopay_offset else 0
            correct_month = self._get_correct_month(account.due_day, offset, selected_month)
            result[account.id]["due"] = (
                    correct_month.replace(day=account.due_day) - datetime.timedelta(days=offset)).isoformat()

        return result
    
    def _next_month(self, date):
        return (date.replace(day=1) + datetime.timedelta(days=40)).replace(day=1)

    def _get_correct_month(self, due_day, offset, month):
        if due_day > offset:
            return month
        else:
            return self._next_month(month)
