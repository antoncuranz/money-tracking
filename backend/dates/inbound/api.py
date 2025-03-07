from typing import Annotated

from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from backend.dates.business.date_service import DateService
from backend.models import User

router = APIRouter(prefix="/api/dates", tags=["Dates"])


@router.get("/{year}/{month}")
def get_due_dates(user: Annotated[User, Depends(get_current_user)],
                  date_service: Annotated[DateService, Depends()],
                  year: int, month: int):
    return date_service.get_dates(user, year, month)
