from flask import abort, Blueprint, g, request

from backend.models import *

api = Blueprint("api", __name__)

@api.before_app_request
def extract_username():
    username = request.headers.get("X-Auth-Request-Preferred-Username")
    if not username:
        abort(401, description="Unauthorized: Username is required.")

    try:
        g.user = User.get(User.name == username)
    except DoesNotExist:
        abort(401, description="Unauthorized: User not found in database.")
