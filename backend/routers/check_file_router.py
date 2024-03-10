from flask import Blueprint, request
from backend.controllers.token_handler import TokenHandler
from backend.controllers.check_image_controller import CheckFileController

check_image_blueprint = Blueprint('image', __name__)


@check_image_blueprint.post("/check_file")
@TokenHandler.verify_access_token
def check_file(user_id: str):
    return CheckFileController(user_id, request).check_image()
