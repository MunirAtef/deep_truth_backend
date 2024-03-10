from typing import Union, Optional

from flask import Request

from backend.controllers.history_controller import HistoryController
from backend.logger.logger import Logger
from deep_fake_model.face_cropper import FaceCropper


class CheckFileController:
    def __init__(self, user_id, check_file_request: Request):
        self.request = check_file_request
        self.file_ext: Union[str, None] = self.request.args.get("ext")
        self.saveToHistory: bool = self.request.args.get("save") == 'true'
        self.user_id = user_id

    def check_file_type(self):
        if self.file_ext in ["png", "jpg", "jpeg"]:
            return self.check_image()
        elif self.file_ext == "mp4":
            return {"message": "videos_will_be_supported_soon"}, 202
        else:
            return {"message": "provide_correct_file_extensions"}, 400

    def check_image(self) -> tuple[Union[dict, list], int]:
        try:
            image_data: bytes = self.request.get_data()

            validation = self._validate_file_size(len(image_data))
            if validation:
                return validation

            model_result = FaceCropper(image_data, self.user_id).check_each_face()
            if model_result is None:
                return {"message": "cannot_reading_the_file"}, 400

            if self.saveToHistory:
                HistoryController.store_to_history(image_data, self.file_ext, self.user_id, model_result)
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
