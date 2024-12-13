from flask import Blueprint, g

from backend.core.service.date_service import DateService

dates = Blueprint("dates", __name__, url_prefix="/api/dates")


@dates.get("/<year>/<month>")
def get_due_dates(year, month, date_service: DateService):
    return date_service.get_dates(g.user, year, month)
