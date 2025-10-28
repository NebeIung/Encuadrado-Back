from flask import Blueprint
from controllers.login_controller import login

login_bp = Blueprint("login", __name__)

@login_bp.route("/login", methods=["POST"])
def login_route():
    return login()