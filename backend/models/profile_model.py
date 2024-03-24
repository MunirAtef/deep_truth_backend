import os
from pathlib import Path
from typing import Optional

from bson import ObjectId
import bcrypt
from pymongo import ReturnDocument
from werkzeug.datastructures import FileStorage

from backend.controllers.history_controller import HistoryController
from backend.models.user_model import UserValidator
from backend.mongodb_connection import MongoDB


class ProfileModel:
    @staticmethod
    def patch_name(user_id: str, new_name: str) -> Optional[str]:
        name_validation: Optional[str] = UserValidator.name_validator(new_name)
        if name_validation:
            return name_validation

        update_result = MongoDB.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"name": new_name.strip()}}
        )

        if update_result.modified_count != 1:
            return "failed_to_update_the_name"
        return None

    @staticmethod
    def patch_pass(user_id: str, old_pass: str, new_pass: str) -> Optional[str]:
        pass_validation: Optional[str] = UserValidator.pass_validator(new_pass)
        if pass_validation:
            return pass_validation

        user = MongoDB.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return "failed_to_load_user"

        if bcrypt.checkpw(old_pass.encode('utf-8'), user["password"].encode('utf-8')):
            update_result = MongoDB.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password": bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode()}}
            )
            print(update_result.modified_count)
            if update_result.modified_count != 1:
                return "failed_to_update_the_password"
        else:
            return "invalid_password"

    @staticmethod
    def patch_picture(user_id: str, image_file: FileStorage):
        ext: str = image_file.filename.split(".")[-1]
        filename: str = HistoryController.unique_filename(ext)
        image_file.save(ProfileModel.get_ppp(filename))
        MongoDB.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"profile_picture": filename}})
        return filename

    @staticmethod
    def delete_picture(user_id: str):
        updated_doc = MongoDB.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$unset": {"profile_picture": 1}},
            return_document=ReturnDocument.BEFORE
        )
        picture: Optional[str] = updated_doc.get("profile_picture")
        try:
            if picture:
                os.remove(ProfileModel.get_ppp(picture))
        except OSError:
            return

    @staticmethod
    def delete_account(user_id: str, password: str) -> Optional[str]:
        query: dict[str, ObjectId] = {"_id": ObjectId(user_id)}
        user = MongoDB.users.find_one(query)
        if not user:
            return "failed_to_load_user"

        if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            MongoDB.users.delete_one(query)
            HistoryController.clear_history(user_id)
            if user.get("profile_picture"):
                os.remove(ProfileModel.get_ppp(user.get("profile_picture")))
        else:
            return "invalid_password"

    @staticmethod
    def get_ppp(filename: str):  # ppp -> Profile Picture Path
        current_dir = str(Path(__file__).parent.parent).replace('\\', '/')
        user_directory = f"{current_dir}/file_repository/profile_pictures"
        if not os.path.exists(user_directory):
            os.makedirs(user_directory, exist_ok=True)
        return f"{user_directory}/{filename}"
