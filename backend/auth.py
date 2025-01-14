import os

from fastapi import HTTPException, Request, status

from backend.models import User
from peewee import DoesNotExist

# TODO: make async once using peewee-async

def get_current_user(request: Request):
    username = os.getenv("OVERWRITE_USER_HEADER") or request.headers.get("X-Auth-Request-Preferred-Username")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Username is required.")

    try:
        return User.get(User.name == username)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: User not found in database.")

def verify_user_header(request: Request):
    get_current_user(request)
    
def require_super_user(request: Request):
    if not get_current_user(request).super_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
