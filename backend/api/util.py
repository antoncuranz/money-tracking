from backend.models import Transaction, Payment, Credit
from playhouse.shortcuts import model_to_dict


def stringify(model, extra_attrs=["account_id"]):
    return model_to_dict(
        model, backrefs=True, exclude=[Transaction.account, Payment.account, Credit.account], extra_attrs=extra_attrs
    )
