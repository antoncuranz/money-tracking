import requests


class GhostfolioClient:
    def __init__(self, bearer_token, base_url="http://localhost:3333"):
        self.bearer_token = bearer_token
        self.base_url = base_url

    def get_bearer_token(self):
        url = f"{self.base_url}/api/v1/auth/anonymous"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        payload = f"accessToken={self.bearer_token}"

        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 201:
            return response.json()["authToken"]
        else:
            response.raise_for_status()

    def import_market_data(self, isin, market_data):
        url = f"{self.base_url}/api/v1/admin/market-data/MANUAL/{isin}"
        headers = {
            'Authorization': f"Bearer {self.get_bearer_token()}",
            'Content-Type': 'application/json',
        }
        payload = {
            "marketData": market_data
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 201:
            return response.json()
        else:
            response.raise_for_status()
