import requests
from requests import JSONDecodeError


class TellerMfaRequired(Exception):
    pass

class ITellerClient:
    def get_account_balances(self, account):
        raise NotImplementedError

    def list_account_transactions(self, account):
        raise NotImplementedError

    def list_accounts(self, account):
        raise NotImplementedError


class TellerClient(ITellerClient):
    _BASE_URL = 'https://api.teller.io'

    def __init__(self, cert):
        self.cert = cert

    def list_accounts(self, account):
        response = self._get('/accounts', account.teller_access_token)
        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def get_account_details(self, account):
        return self._get(f'/accounts/{account.teller_id}/details', account.teller_access_token)

    def get_account_balances(self, account):
        response = self._get(f'/accounts/{account.teller_id}/balances', account.teller_access_token)
        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def list_account_transactions(self, account):
        response = self._get(f'/accounts/{account.teller_id}/transactions', account.teller_access_token)
        if response.ok:
            return response.json()
        else:
            try:
                json = response.json()
                if "error" in json and json["error"]["code"] == "enrollment.disconnected.user_action.mfa_required":
                    raise TellerMfaRequired()
            except JSONDecodeError:
                pass
            response.raise_for_status()

    def list_account_payees(self, account, scheme):
        return self._get(f'/accounts/{account.teller_id}/payments/{scheme}/payees', account.teller_access_token)

    def create_account_payee(self, account, scheme, data):
        return self._post(f'/accounts/{account.teller_id}/payments/{scheme}/payees', account.teller_access_token, data)

    def create_account_payment(self, account, scheme, data):
        return self._post(f'/accounts/{account.teller_id}/payments/{scheme}', account.teller_access_token, data)

    def _get(self, path, access_token):
        return self._request('GET', path, access_token)

    def _post(self, path, data, access_token):
        return self._request('POST', path, access_token, data)

    def _request(self, method, path, access_token, data=None):
        url = self._BASE_URL + path
        auth = (access_token, '')
        return requests.request(method, url, json=data, cert=self.cert, auth=auth)
