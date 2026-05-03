import base64
import json
import os
import traceback
from typing import Annotated

from fastapi import HTTPException, Depends, Request, status
from sqlmodel import Session, select

from models import User, get_session


# TODO: make async


def _extract_username(request: Request) -> str | None:
    username = os.getenv("OVERWRITE_USER_HEADER")
    if username:
        return username

    authorization = request.headers.get("Authorization")
    if authorization:
        scheme, _, token = authorization.partition(" ")
        if scheme != "Bearer" or not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Bearer token is required.")

        try:
            _, payload, _ = token.split(".")
            padding = "=" * (-len(payload) % 4)
            claims = json.loads(base64.urlsafe_b64decode(payload + padding))
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Invalid bearer token.")

        username = claims.get("preferred_username")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Username is required.")

        return username

    return request.headers.get("X-Auth-Request-Preferred-Username")

def get_current_user(request: Request, session: Annotated[Session, Depends(get_session)]):
    username = _extract_username(request)
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
