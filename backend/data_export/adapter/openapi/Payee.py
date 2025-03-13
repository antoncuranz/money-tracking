from typing import *

from pydantic import BaseModel, Field


class Payee(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="id", default=None)

    name: str = Field(validation_alias="name")

    category: Optional[str] = Field(validation_alias="category", default=None)

    transfer_acct: Optional[str] = Field(validation_alias="transfer_acct", default=None)
