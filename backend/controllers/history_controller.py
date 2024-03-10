import base64
import os
import random
import shutil
import string
import time
from pathlib import Path
from flask import request, send_file

from backend.logger.logger import Logger
from backend.models.histoy_file_model import HistoryFileModel


class HistoryController:
    @staticmethod
    def store_to_history(image_data: bytes, file_ext: str, user_id: str, result):
        try:
            filename = HistoryController._unique_filename(file_ext)
            image_path: str = HistoryController._get_file_path(user_id, filename)

            with open(image_path, "wb") as f:
                f.write(image_data)

            HistoryFileModel(filename, user_id, result).save_to_db()

            return filename, 200
        except Exception as e:
            print(type(e), e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def _get_file_path(user_id: str, filename: str) -> str:
        current_dir = str(Path(__file__).parent.parent).replace('\\', '/')
        user_directory = f"{current_dir}/files_history/{user_id}"

        if not os.path.exists(user_directory):
            os.makedirs(user_directory, exist_ok=True)

        return f"{user_directory}/{filename}"

    @staticmethod
    def get_history_data(user_id: str):
        try:
            result = HistoryFileModel.get_user_file(user_id)
            print(result)
            return result, 200
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def get_file(user_id: str):
        try:
            filename = request.args.get("filename")
            file_path = HistoryController._get_file_path(user_id, filename)

            if not os.path.exists(file_path):
                return {"message": "file_not_found"}, 404

            return send_file(file_path, mimetype=HistoryController._get_mimetype(filename))
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def _get_mimetype(filename: str) -> str:
        ext: str = filename.split(".")[-1].lower()

        if ext in ["png", "jpg", "jpeg"]:
            return f"image/{ext}"
        elif ext == "mp4":
            return "video/mp4"
        else:
            return "application/octet-stream"

    @staticmethod
    def delete_file(user_id):
        try:
            filename = request.args.get("filename")
            if filename is None:
                return {"message": "filename_unprovided"}, 400
            file_path: str = HistoryController._get_file_path(user_id, filename)
            HistoryFileModel.delete_file(user_id, filename)
            os.remove(file_path)
            return filename, 200
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def clear_history(user_id):
        try:
            file_path: str = HistoryController._get_file_path(user_id, "")[:-1]
            shutil.rmtree(file_path)
            result: int = HistoryFileModel.delete_user_files(user_id)

            return {"deletedFilesCount": result}, 200
        except OSError:
            return {"message": "failed_to_clear_history"}, 500
        except Exception as e:
            Logger.error(request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def _unique_filename(ext: str) -> str:
        num = int(time.time() * 1000)
        time_bytes: bytes = num.to_bytes((num.bit_length() + 7) // 8, byteorder='big')
        time_base64: str = base64.b64encode(time_bytes).decode('utf-8')
        random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        return f"{time_base64}{random_chars}.{ext}"
