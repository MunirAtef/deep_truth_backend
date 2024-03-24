import werkzeug
from werkzeug.exceptions import UnsupportedMediaType

from backend.logger.logger import Logger
from backend.models.user_model import UserModel
from flask import request


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
            print(f"{name = }, {email = }, {password = }")

            user_json = UserModel(name, email, password)
            print(user_json.to_json())
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
