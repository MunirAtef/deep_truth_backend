import re
import time
from typing import Union, Optional

from passlib.hash import bcrypt

from bson import ObjectId

from backend.controllers.token_handler import TokenHandler
from backend.mongodb_connection import MongoDB


class UserModel:
    def __init__(self, name: Optional[str], email: Optional[str], password: Optional[str]):
        self.name: Optional[str] = name
        self.email: Optional[str] = email
        self.password: Optional[str] = password
        self.role: str = "user"
        self.created_at: int = int(time.time())

    def to_json(self) -> dict[str, Union[str, int]]:
        return {
            "name": self.name,
            "email": self.email,
            "password": bcrypt.hash(self.password),
            "role": self.role,
            "created_at": self.created_at
        }

    @staticmethod
    def _format_response(raw_result: dict) -> dict[str, Union[str, int]]:
        user_id = str(raw_result["_id"])

        del raw_result["_id"]
        del raw_result["password"]

        raw_result["id"] = user_id
        raw_result["access_token"] = TokenHandler.generate_access_token(user_id)
        raw_result["refresh_token"] = TokenHandler.generate_refresh_token(user_id)

        return raw_result

    def save(self) -> tuple[dict, bool]:
        message: Optional[str] = UserValidator.valid_all(self)
        print(message)
        if message:
            return {"message": message}, False
        user_json: dict[str, Union[str, int]] = self.to_json()
        MongoDB.users.insert_one(user_json)
        return self._format_response(user_json), True

    @staticmethod
    def login_user(email, password) -> tuple[dict, int]:
        if not email or not password:
            return {"message": "provide_correct_email_and_password"}, 400
        user = MongoDB.users.find_one({"email": email})
        if user and bcrypt.verify(password, user["password"]):
            return UserModel._format_response(user), 200
        else:
            return {"message": "invalid_credentials"}, 401

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

        if bcrypt.verify(old_pass, user["password"]):
            update_result = MongoDB.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password": bcrypt.hash(new_pass)}}
            )
            print(update_result.modified_count)
            if update_result.modified_count != 1:
                return "failed_to_update_the_name"
        else:
            return "invalid_password"


class UserValidator:
    @staticmethod
    def name_validator(name: Optional[str]) -> Optional[str]:
        if not name or name.strip() == "":
            return "name_cannot_be_empty"
        if len(name.strip()) > 100:
            return "name_is_too_long"
        return None

    @staticmethod
    def email_validator(email: Optional[str]) -> Optional[str]:
        if not email or email.strip() == "":
            return "email_cannot_be_empty"

        email = email.strip().lower()
        if len(email) > 100:
            return "email_is_too_long"

        email_regex: str = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(email_regex, email):
            return "invalid_email_format"
        if MongoDB.users.find_one({"email": email}):
            return "email_already_registered"

        return None

    @staticmethod
    def pass_validator(password: Optional[str]) -> Optional[str]:
        if not password:
            return "password_is_required"
        pass_len: int = len(password)
        if pass_len < 8:
            return "password_is_too_short"
        if pass_len > 30:
            return "password_is_too_long"
        return None

    @staticmethod
    def valid_all(user_model: UserModel):
        vld_msg: Optional[str]
        vld_msg = UserValidator.name_validator(user_model.name)
        if vld_msg:
            return vld_msg

        vld_msg = UserValidator.email_validator(user_model.email)
        if vld_msg:
            return vld_msg

        vld_msg = UserValidator.pass_validator(user_model.password)
        if vld_msg:
            return vld_msg

        # messages = [
        #     UserValidator.email_validator(user_model.email),
        #     UserValidator.name_validator(user_model.name),
        #     UserValidator.pass_validator(user_model.password)
        # ]
        # print(messages)
        # for message in messages:
        #     if message:
        #         return message
        # return None
