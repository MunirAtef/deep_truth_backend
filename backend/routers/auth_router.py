from flask import Blueprint
from backend.controllers.auth_controller import AuthController
from backend.controllers.token_handler import TokenHandler

auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.post("login")
def login_with_email():
    return AuthController.login_with_email()


@auth_blueprint.post("signup")
def signup_with_email():
    return AuthController.signup_with_email()


@auth_blueprint.post("refresh_access_token")
def refresh_access_token():
    return TokenHandler.verify_refresh_token()
