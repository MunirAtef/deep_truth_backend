
from flask import Blueprint
from backend.controllers.profile_controller import ProfileController
from backend.controllers.token_handler import TokenHandler

profile_blueprint = Blueprint('profile', __name__)


@profile_blueprint.post("update_name")
@TokenHandler.verify_access_token
def update_name(user_id: str):
    return ProfileController.patch_name(user_id)

@profile_blueprint.post("update_password")
@TokenHandler.verify_access_token
def update_password(user_id: str):
    return ProfileController.patch_password(user_id)

@profile_blueprint.post("update_picture")
@TokenHandler.verify_access_token
def update_picture(user_id: str):
    return ProfileController.patch_picture(user_id)

@profile_blueprint.post("delete_picture")
@TokenHandler.verify_access_token
def delete_picture(user_id: str):
    return ProfileController.delete_picture(user_id)

@profile_blueprint.post("delete_account")
@TokenHandler.verify_access_token
def delete_account(user_id: str):
    return ProfileController.delete_account(user_id)
