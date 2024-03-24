from flask import Blueprint

from backend.controllers.token_handler import TokenHandler
from backend.controllers.history_controller import HistoryController

history_blueprint = Blueprint('history', __name__)


@history_blueprint.get("/history_data")
@TokenHandler.verify_access_token
def get_history_data(user_id):
    print(user_id)
    return HistoryController.get_history_data(user_id)


@history_blueprint.get("/file")
@TokenHandler.verify_access_token
def get_image_file(user_id):
    print(user_id)
    return HistoryController.get_file(user_id)


@history_blueprint.delete("/file")
@TokenHandler.verify_access_token
def delete_file(user_id):
    print(user_id)
    return HistoryController.delete_file(user_id)


@history_blueprint.delete("/clear_history")
@TokenHandler.verify_access_token
def delete_all_file(user_id):
    print(user_id)
    result = HistoryController.clear_history(user_id)
    print(result)
    return result
