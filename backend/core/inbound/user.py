from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import SQLModel

from auth import get_current_user
from models import User

router = APIRouter(prefix="/api/user", tags=["User"])

@router.get("name", response_model=str)
def get_username(user: Annotated[User, Depends(get_current_user)]):
    return user.name


@router.get("/super", response_model=bool)
def get_username(user: Annotated[User, Depends(get_current_user)]):
    return user.super_user


class UserTO(SQLModel):
    id: int
    name: str
    super_user: bool = False

@router.get("", response_model=UserTO)
def get_user(user: Annotated[User, Depends(get_current_user)]):
    return user
