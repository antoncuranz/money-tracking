import json
from typing import Annotated, List

import plaid
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, SQLModel

from auth import get_current_user
from core.inbound.user import UserTO
from data_import.business.plaid_service import PlaidService
from models import get_session, User

router = APIRouter(prefix="/api/import/plaid", tags=["Plaid Connection"])

class PlaidLinkTokenTO(SQLModel):
    link_token: str

@router.post("/create_link_token", response_model=PlaidLinkTokenTO)
def create_link_token(plaid_service: Annotated[PlaidService, Depends()]):
    try:
        return plaid_service.create_link_token()
    except plaid.ApiException as e:
        print(e)
        return json.loads(e.body)


@router.post("/exchange_token", status_code=status.HTTP_204_NO_CONTENT)
def exchange_token(user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)],
                   plaid_service: Annotated[PlaidService, Depends()],
                   public_token: str):
    try:
        plaid_service.exchange_token(session, user, public_token)
    except plaid.ApiException as e:
        print(e)
        return json.loads(e.body)


class PlaidAccountTO(SQLModel):
    id: int
    name: str
    plaid_account_id: str
    connection_id: int
    
class PlaidConnectionTO(SQLModel):
    id: int
    user: UserTO
    name: str | None
    plaid_item_id: str
    plaid_accounts: List[PlaidAccountTO]

@router.get("/connections", response_model=List[PlaidConnectionTO])
def get_connections(user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)],
                      plaid_service: Annotated[PlaidService, Depends()]):
    return plaid_service.get_connections(session, user)


@router.post("/connections/{connection_id}/discover", status_code=status.HTTP_204_NO_CONTENT)
def discover_accounts(user: Annotated[User, Depends(get_current_user)],
                   session: Annotated[Session, Depends(get_session)],
                   plaid_service: Annotated[PlaidService, Depends()],
                   connection_id: int):
    plaid_service.discover_accounts(session, user, connection_id)
    
    
@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_connection(user: Annotated[User, Depends(get_current_user)],
                      session: Annotated[Session, Depends(get_session)],
                      plaid_service: Annotated[PlaidService, Depends()],
                      connection_id: int):
    plaid_service.delete_connection(session, user, connection_id)
