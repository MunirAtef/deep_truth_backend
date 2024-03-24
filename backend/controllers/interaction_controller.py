import os

from bson import ObjectId
from flask import request, send_file
from typing import Optional

from backend.controllers.history_controller import HistoryController
from backend.models.histoy_file_model import HistoryFileModel
from backend.models.profile_model import ProfileModel
from backend.models.user_model import UserModel
from backend.mongodb_connection import MongoDB
from backend.logger.logger import Logger


class InteractionController:
    @staticmethod
    def search_users(user_id: str):
        try:
            search_term: str = request.args.get("search_term")
            query = {"name": {"$regex": search_term, "$options": "i"}, "_id": {"$ne": ObjectId(user_id)}}
            response = MongoDB.users.find(query).limit(20)
            return [UserModel.format_response(raw_user, same_user=False) for raw_user in response], 200
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def get_public_history(user_id):
        try:
            target_user_id: str = request.args.get("target_id")
            return HistoryFileModel.get_user_files(target_user_id, same_user=user_id == target_user_id), 200
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500


    @staticmethod
    def get_profile_picture():
        try:
            filename: Optional[str] = request.args.get("filename")
            if not filename:
                return {"message": "provide_filename"}, 400
            filepath: str = ProfileModel.get_ppp(filename)
            print(filepath)
            if not os.path.exists(filepath):
                return {"message": "file_not_exists"}, 404

            ext: str = filename.split('.')[-1]
            return send_file(filepath, mimetype=f"image/{ext}"), 200
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def history_file_another_user():
        try:
            user_id: str = request.args.get("user_id")
            filename: str = request.args.get("filename")
            result = MongoDB.history.find_one({"user_id": user_id, "filename": filename})
            if not result:
                return {"message": "file_not_found"}, 404
            if result["access"] != "public":
                return {"message": "file_not_public"}, 401
            filepath: str = HistoryController.get_file_path(user_id, filename)
            if not os.path.exists(filepath):
                return {"message": "file_not_found"}, 404
            return send_file(filepath, mimetype=HistoryController.mimetype(filename)), 200
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500
