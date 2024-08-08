from backend.models import Transaction, Payment, Credit
from playhouse.shortcuts import model_to_dict


def stringify(model, extra_attrs=["account_id"]):
    return model_to_dict(
        model, backrefs=True, exclude=[Transaction.account, Payment.account, Credit.account], extra_attrs=extra_attrs
    )


def parse_boolean(bool_str):
    try:
        if bool_str.lower() == "true":
            return True
        elif bool_str.lower() == "false":
            return False
        else:
            print(f"Unable to parse boolean value of \"{bool_str}\"")
            return None
    except AttributeError:
        return None
