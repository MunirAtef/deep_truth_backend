import werkzeug
from werkzeug.exceptions import UnsupportedMediaType

from backend.logger.logger import Logger
from backend.models.user_model import UserModel
from flask import request
from typing import Optional


class AuthController:
    @staticmethod
    def login_with_email():
        try:
            body = request.get_json()
            email = body.get("email")
            password = body.get("password")

            return UserModel.login_user(email, password)
        except UnsupportedMediaType:
            return {"message": "invalid_body_sent"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def signup_with_email():
        try:
            body = request.get_json()
            name = body.get("name")
            email = body.get("email")
            password = body.get("password")

            user_json = UserModel(name, email, password)
            response, passed = user_json.save()
            if passed:
                return response, 200
            return response, 400
        except KeyError:
            return {"message": "missing_required_keys"}, 400
        except werkzeug.exceptions.BadRequest:
            return {"message": "bad_request"}, 400
        except UnsupportedMediaType:
            return {"message": "invalid_body_sent"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def patch_name(user_id: str):
        try:
            new_name = request.get_json().get("name")
            result: Optional[str] = UserModel.patch_name(user_id, new_name)
            if not result:
                return "named_updated", 200
            return {"message": result}, 400
        except UnsupportedMediaType:
            return {"message": "invalid_body_sent"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def patch_password(user_id: str):
        try:
            body = request.get_json()
            old_pass = body.get("password")
            new_pass = body.get("new_password")
            result: Optional[str] = UserModel.patch_pass(user_id, old_pass, new_pass)
            if not result:
                return "password_updated", 200
            return result, 400
        except UnsupportedMediaType:
            return {"message": "invalid_body_sent"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500
