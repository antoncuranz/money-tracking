import os
import traceback
from typing import Annotated

from fastapi import HTTPException, Depends, Request, status
from sqlmodel import Session, select

from backend.models import User, get_session


# TODO: make async

def get_current_user(request: Request, session: Annotated[Session, Depends(get_session)]):
    username = os.getenv("OVERWRITE_USER_HEADER") or request.headers.get("X-Auth-Request-Preferred-Username")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Username is required.")

    try:
        stmt = select(User).where(User.name == username)
        return session.exec(stmt).one()
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: User not found in database.")

def verify_user_header(request: Request, session: Annotated[Session, Depends(get_session)]):
    get_current_user(request, session)
    
def require_super_user(request: Request, session: Annotated[Session, Depends(get_session)]):
    if not get_current_user(request, session).super_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
