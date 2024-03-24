from typing import Union, Optional

from flask import Request
from backend.controllers.history_controller import HistoryController
from backend.logger.logger import Logger
from deep_fake_model.face_cropper import FaceCropper
from werkzeug.datastructures import FileStorage


class CheckFileController:
    def __init__(self, user_id, check_file_request: Request):
        self.request = check_file_request
        self.image_file: Optional[FileStorage] = self.request.files.get("ftc")
        self.file_ext: Union[str, None] = self.image_file.filename.split(".")[-1]
        self.save_to_history: bool = self.request.args.get("save") == 'true'
        self.user_id = user_id
        self.file_th: str = self.get_file_th()

    def get_file_th(self):
        file_th: Optional[str] = self.request.args.get("th")
        if not file_th:
            file_th = '0'
        return file_th

    def get_access_rule(self) -> str:
        if self.request.args.get("access") == "public":
            return "public"
        return "private"

    def check_file_type(self):
        if self.file_ext in ["png", "jpg", "jpeg"]:
            return self.check_image()
        elif self.file_ext == "mp4":
            return {"message": "videos_will_be_supported_soon"}, 202
        else:
            return {"message": "provide_correct_file_extensions"}, 400

    def check_image(self) -> tuple[Union[dict, list], int]:
        try:
            if not self.image_file:
                return {"message": "image_not_provided"}, 400
            image_data: bytes = self.image_file.stream.read()
            validation = self._validate_file_size(len(image_data))
            if validation:
                return validation

            model_result = FaceCropper(image_data, self.user_id, self.file_th).check_each_face()
            if model_result is None:
                return {"message": "cannot_reading_the_file"}, 400

            if self.save_to_history:
                HistoryController.store_to_history(
                    image_data=image_data,
                    file_ext=self.file_ext,
                    user_id=self.user_id,
                    result=model_result,
                    access=self.get_access_rule()
                )
            return model_result, 200
        except Exception as e:
            Logger.error(self.request, e)
            return {"message": "internal_server_error"}, 500

    @staticmethod
    def _validate_file_size(file_size: int) -> Optional[tuple[dict[str, str], int]]:
        if file_size == 0:
            return {"message": "no_file_uploaded"}, 400
        if file_size < 100:
            return {"message": "invalid_uploaded_file"}, 400
        if file_size > 40000000:
            return {"message": "file_size_exceeds_40MG"}, 400
        return None
