from flask import Blueprint, jsonify
from flask_security import auth_required


bp_api_auth = Blueprint("bp_api_auth", __name__)


@bp_api_auth.route("/api/auth/check_logged", methods=["GET"])
@auth_required()
def check_logged():
    """
    Check if logged in
    ---
    tags:
        - Auth
    responses:
        200:
            description: logged in status
    """
    return jsonify("OK_LOGGED_IN")
