import bson
from flask import request
from typing import Optional

from backend.logger.logger import Logger
from backend.models.connection_model import ConnectionModel


class ConnectionController:
    @staticmethod
    def send_request(user_id: str):
        try:
            recipient_id: Optional[str] = request.args.get("recipient")
            if not recipient_id:
                return {"message": "recipient_id_not_provided"}, 400
            conn_model = ConnectionModel(user_id, recipient_id)
            result = conn_model.save()
            if result:
                return result
            return "request_sent", 200
        except bson.errors.InvalidId:
            return {"message": "invalid_recipient_id"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def accept_request(user_id: str):
        try:
            requester_id: Optional[str] = request.args.get("requester")
            if not requester_id:
                return {"message": "requester_id_not_provided"}, 400
            is_accepted = ConnectionModel.accept(user_id, requester_id)
            if is_accepted:
                return "request_accepted", 200
            return {"message": "failed_to_update_request"}, 400
        except bson.errors.InvalidId:
            return {"message": "invalid_requester_id"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def remove_received_request(user_id: str):
        try:
            requester_id: Optional[str] = request.args.get("requester")
            if not requester_id:
                return {"message": "requester_id_not_provided"}, 400
            ConnectionModel.remove_request(user_id, requester_id)
            return "request_removed", 200
            # return {"message": "failed_to_remove_request"}, 400
        except bson.errors.InvalidId:
            return {"message": "invalid_requester_id"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def undo_request(user_id: str):
        try:
            recipient_id: Optional[str] = request.args.get("recipient")
            if not recipient_id:
                return {"message": "recipient_id_not_provided"}, 400
            ConnectionModel.undo_request(user_id, recipient_id)
            return "request_undone", 200
            # return {"message": "failed_to_undo_request"}, 400
        except bson.errors.InvalidId:
            return {"message": "invalid_recipient_id"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def connections(user_id: str):
        try:
            return ConnectionModel.connections(user_id), 200
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def relation(user_id):
        try:
            target_id: Optional[str] = request.args.get("target")
            if not target_id:
                return {"message": "target_user_id_not_provided"}, 400
            if user_id == target_id:
                return {"message": "invalid_target_selection"}, 409
            result = ConnectionModel.get_relation(user_id, target_id)
            if result:
                return result, 200
            return "no_relation", 202
        except bson.errors.InvalidId:
            return {"message": "invalid_target_user_id"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def inbound_requests(user_id: str):
        try:
            result = ConnectionModel.inbound_requests(user_id)
            return result, 200
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def outbound_requests(user_id: str):
        try:
            result = ConnectionModel.outbound_requests(user_id)
            return result, 200
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500
