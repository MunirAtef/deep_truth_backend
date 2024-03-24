
from flask import Blueprint

from backend.controllers.token_handler import TokenHandler
from backend.controllers.interaction_controller import InteractionController

interact_blueprint = Blueprint('interact', __name__)


@interact_blueprint.get("users")
@TokenHandler.verify_access_token
def get_users_by_sub_name(user_id: str):
    return InteractionController.search_users(user_id)


@interact_blueprint.get("history")
@TokenHandler.verify_access_token
def get_another_user_history(user_id: str):
    return InteractionController.get_public_history(user_id)


@interact_blueprint.get("profile_picture")
def get_profile_picture():
    return InteractionController.get_profile_picture()

@interact_blueprint.get("history_file")
def get_history_file():
    return InteractionController.history_file_another_user()

