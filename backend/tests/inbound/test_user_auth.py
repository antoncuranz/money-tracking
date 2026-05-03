import base64
import json

from fastapi.testclient import TestClient
from sqlmodel import Session

from models import User


def _jwt(payload: dict) -> str:
    header = {"alg": "none", "typ": "JWT"}
    segments = []
    for part in (header, payload):
        encoded = base64.urlsafe_b64encode(json.dumps(part).encode()).decode().rstrip("=")
        segments.append(encoded)
    return ".".join([*segments, "signature"])


def test_get_current_user_reads_existing_user_from_bearer_token(session: Session, client: TestClient):
    session.add(User(name="alice"))
    session.commit()

    response = client.get(
        "/api/user",
        headers={"Authorization": f"Bearer {_jwt({'preferred_username': 'alice'})}"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "alice"
