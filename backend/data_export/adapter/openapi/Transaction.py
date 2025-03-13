from typing import *

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """
    None model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    id: Optional[str] = Field(validation_alias="id", default=None)

    account: Optional[str] = Field(validation_alias="account", default=None)

    date: Optional[str] = Field(validation_alias="date", default=None)

    amount: Optional[int] = Field(validation_alias="amount", default=None)

    payee: Optional[str] = Field(validation_alias="payee", default=None)

    payee_name: Optional[str] = Field(validation_alias="payee_name", default=None)

    imported_payee: Optional[str] = Field(validation_alias="imported_payee", default=None)

    category: Optional[str] = Field(validation_alias="category", default=None)

    notes: Optional[str] = Field(validation_alias="notes", default=None)

    imported_id: Optional[str] = Field(validation_alias="imported_id", default=None)

    transfer_id: Optional[str] = Field(validation_alias="transfer_id", default=None)

    cleared: Optional[bool] = Field(validation_alias="cleared", default=None)

    subtransactions: Optional[List[Optional["Transaction"]]] = Field(validation_alias="subtransactions", default=None)
