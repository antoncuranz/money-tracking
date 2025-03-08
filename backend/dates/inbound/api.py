from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from auth import get_current_user
from dates.business.date_service import DateService
from models import User, get_session

router = APIRouter(prefix="/api/dates", tags=["Dates"])


@router.get("/{year}/{month}")
def get_due_dates(user: Annotated[User, Depends(get_current_user)],
                  session: Annotated[Session, Depends(get_session)],
                  date_service: Annotated[DateService, Depends()],
                  year: int, month: int):
    return date_service.get_dates(session, user, year, month)
