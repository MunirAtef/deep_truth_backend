from flask import Blueprint
from backend.controllers.connection_controller import ConnectionController
from backend.controllers.token_handler import TokenHandler

connection_blueprint = Blueprint('connect', __name__)

@connection_blueprint.post("send_request")
@TokenHandler.verify_access_token
def send_request(user_id: str):
    return ConnectionController.send_request(user_id)


@connection_blueprint.post("accept_request")
@TokenHandler.verify_access_token
def accept_request(user_id: str):
    return ConnectionController.accept_request(user_id)


@connection_blueprint.post("remove_request")
@TokenHandler.verify_access_token
def remove_request(user_id: str):
    return ConnectionController.remove_received_request(user_id)

@connection_blueprint.post("undo_request")
@TokenHandler.verify_access_token
def undo_request(user_id: str):
    return ConnectionController.undo_request(user_id)

@connection_blueprint.get("connections")
@TokenHandler.verify_access_token
def connections(user_id: str):
    return ConnectionController.connections(user_id)

@connection_blueprint.get("relation")
@TokenHandler.verify_access_token
def relation(user_id: str):
    return ConnectionController.relation(user_id)


@connection_blueprint.get("outbound_requests")
@TokenHandler.verify_access_token
def outbound_requests(user_id: str):
    return ConnectionController.outbound_requests(user_id)

@connection_blueprint.get("inbound_requests")
@TokenHandler.verify_access_token
def inbound_requests(user_id: str):
    return ConnectionController.inbound_requests(user_id)
