from backend.config import config
import requests
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from datetime import datetime
from pebble import concurrent
from paho.mqtt import subscribe

MQTT_TOPIC = "postfix/quiltt"
MQTT_CONFIG = {
    "hostname": config.mqtt_host,
    "port": 443,
    "transport": "websockets",
    "auth": {"username": config.mqtt_user, "password": config.mqtt_passwd},
    "tls": {"ca_certs": "root.pem"}
}

class IQuilttClient:
    def get_account_balance(self, account_import_id, token):
        raise NotImplementedError

    def get_account_transactions(self, account_import_id, token):
        raise NotImplementedError

    def retrieve_session_token(self):
        raise NotImplementedError


class QuilttClient(IQuilttClient):
    def __init__(self):
        self.auth_headers = {}
        transport = AIOHTTPTransport(url="https://api.quiltt.io/v1/graphql", headers=self.auth_headers)
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def get_account_balance(self, account_import_id, token):
        query = gql("""
            query GetBalance($accountId: ID!) {
              account(id: $accountId) {
                balance {
                  current
                }
                connection {
                  status
                }
              }
            }
        """)

        result = self._execute_with_token(token, query, variable_values={"accountId": account_import_id})
        if result["account"]["connection"]["status"] not in {"SYNCED", "SYNCING"}:
            raise RuntimeError("Connection degraded")
        return result["account"]["balance"]["current"]

    def get_account_transactions(self, account_import_id, token):
        query = gql("""
            query GetTransactions($accountId: ID!) {
              account(id: $accountId) {
                connection {
                  status
                }
                transactions(filter: {status: POSTED, date_gt: "2024-12-15"}) {
                  nodes {
                    amount
                    currencyCode
                    date
                    description
                    status
                    remoteData {
                      mx {
                        transaction {
                          response {
                            originalDescription
                          }
                          id
                        }
                      }
                    }
                  }
                }
              }
            }
        """)

        result = self._execute_with_token(token, query, variable_values={"accountId": account_import_id})
        if result["account"]["connection"]["status"] not in {"SYNCED", "SYNCING"}:
            raise RuntimeError("Connection degraded")
        return [gql_tx for gql_tx in result["account"]["transactions"]["nodes"]]

    def retrieve_session_token(self):
        future = self._retrieve_passcode()
        rsp = requests.post("https://auth.quiltt.io/v1/users/session", json=self._build_request_body())
        if not rsp.ok:
            raise RuntimeError("Error requesting passcode")

        try:
            passcode = future.result()
        except TimeoutError as error:
            raise RuntimeError("Error retrieving passcode within %d seconds" % error.args[1])

        rsp = requests.put("https://auth.quiltt.io/v1/users/session", json=self._build_request_body(passcode))
        if not rsp.ok:
            raise RuntimeError("Error requesting token")

        json_rsp = rsp.json()
        return json_rsp["token"], datetime.fromtimestamp(json_rsp["expiration"])

    @concurrent.process(timeout=20)
    def _retrieve_passcode(self):
        msg = subscribe.simple(MQTT_TOPIC, **MQTT_CONFIG)
        passcode = msg.payload.decode("utf-8")
        return passcode

    def _build_request_body(self, passcode=None):
        body = {"session": {"clientId": "api_142yndJj4xAAywindxUeLZZ", "email": "anton@curanz.de"}}
        if passcode is not None:
            body["session"]["passcode"] = passcode
        return body

    def _execute_with_token(self, token, query, **kwargs):
        self.auth_headers["Authorization"] = "Bearer " + token
        return self.client.execute(query, **kwargs)
