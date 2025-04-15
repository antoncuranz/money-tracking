import os
import re
import sys

import requests

actual_base_url = os.getenv("ACTUAL_BASE_URL", "http://localhost:5007")
actual_api_key = os.getenv("ACTUAL_API_KEY")
actual_sync_id = os.getenv("ACTUAL_SYNC_ID")
actual_encryption_passwd = os.getenv("ACTUAL_ENCRYPTION_PASSWD")
actual_account_id = os.getenv("ACTUAL_ACCOUNT_ID")

testmail_api_key = os.getenv("TESTMAIL_API_KEY")
testmail_namespace = os.getenv("TESTMAIL_NAMESPACE")

url = f"https://api.testmail.app/api/json?apikey={testmail_api_key}&namespace={testmail_namespace}"
regex = r"<div style=\"[^\"]*\">\s*(\d\d)\.(\d\d)\.(\d\d\d\d)([^<]*)<\/div>.*<div style=\"[^\"]*\">\s*€(\d+,\d\d)\s*<\/div>"


def import_transaction(transaction):
    url = f"{actual_base_url}/v1/budgets/{actual_sync_id}/accounts/{actual_account_id}/transactions/import"
    headers = {
        'x-api-key': actual_api_key,
        "budget-encryption-password": actual_encryption_passwd,
        'Content-Type': 'application/json',
    }
    payload = {
        "transactions": [transaction]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.ok:
        return response.json()
    else:
        response.raise_for_status()


try:
    response = requests.get(url).json()
except Exception as e:
    print("Error fetching mails!")
    print(e)
    sys.exit(1)

for mail in response["emails"]:
    html = mail["html"]
    imported_id = mail["messageId"]

    match = re.search(regex, html, re.DOTALL)
    if not match:
        print(f"Error matching regex for mail {imported_id}!")

        if "Benachrichtigung über einen neuen Kartenumsatz" in mail["subject"]:
            sys.exit(1)
        else:
            continue  # might be a test mail

    amount = int(match.group(5).replace(",", ""))
    date = f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
    description = " ".join(line.strip() for line in match.group(4).splitlines()).strip()

    print("ID: " + imported_id)
    print("Amount: " + str(amount))
    print("Date: " + date)
    print("Description: " + description)

    try:
        import_transaction({
            "account": actual_account_id,
            "amount": -amount,
            "payee_name": description,
            "date": date,
            "cleared": True
        })
    except Exception as e:
        print("Error importing transaction!")
        print(e)
        sys.exit(1)

    print("===")
