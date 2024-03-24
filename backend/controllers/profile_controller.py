
from flask import request
from typing import Optional

from werkzeug.exceptions import UnsupportedMediaType
from werkzeug.datastructures import FileStorage

from backend.models.profile_model import ProfileModel
from backend.logger.logger import Logger

class ProfileController:
    @staticmethod
    def patch_name(user_id: str):
        try:
            new_name = request.get_json().get("name")
            result: Optional[str] = ProfileModel.patch_name(user_id, new_name)
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
            result: Optional[str] = ProfileModel.patch_pass(user_id, old_pass, new_pass)
            if not result:
                return "password_updated", 200
            return {"message": result}, 400
        except UnsupportedMediaType:
            return {"message": "invalid_body_sent"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def patch_picture(user_id: str):
        try:
            new_picture: Optional[FileStorage] = request.files.get("profile_picture")
            if not new_picture:
                return {"message": "profile_picture_not_provided"}, 400
            filename: str = ProfileModel.patch_picture(user_id, new_picture)
            return filename, 200
        except UnsupportedMediaType:
            return {"message": "invalid_body_sent"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def delete_picture(user_id: str):
        try:
            ProfileModel.delete_picture(user_id)
            return "picture_deleted", 200
        except OSError:
            return {"message": "error_deleting_image_file"}, 500
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def delete_account(user_id: str):
        try:
            password: Optional[str] = request.get_json().get("password")
            if not password:
                return {"message": "empty_password"}

            result: Optional[str] = ProfileModel.delete_account(user_id, password)
            if not result:
                return "account_deleted", 200
            return {"message": result}, 400
        except UnsupportedMediaType:
            return {"message": "invalid_body_sent"}, 400
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500
