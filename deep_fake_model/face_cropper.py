import os
import time
from typing import Union, Sequence, Optional

import cv2
import numpy as np

from deep_fake_model.deep_fake_images import is_fake


class FaceCropper:
    def __init__(self, image_bytes: bytes, temp_dir, file_th: str):
        self.image_array = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        self.width = len(self.image_array[0])
        self.height = len(self.image_array)
        self.file_th = file_th

        self.temp_dir = temp_dir
        self.faces = self.get_faces()

    def get_faces(self) -> Optional[Sequence[Sequence[int]]]:
        try:
            gray_image = cv2.cvtColor(self.image_array, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            return face_cascade.detectMultiScale(gray_image, scaleFactor=1.3, minNeighbors=5)
        except cv2.error:
            return None

    def check_each_face(self) -> Optional[list[dict[str, Union[list[float], str]]]]:
        if self.faces is None:
            return None

        faces: list[dict[str, Union[list[float], str]]] = []

        for face in self.faces:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            face_path = f'{current_dir}/temp_faces/{self.temp_dir}{str(int(time.time() * 1000))[-6:-1]}.png'
            start_x, start_y, width, height = face
            cropped_face = self.image_array[start_y:start_y + height, start_x:start_x + width]
            cv2.imwrite(face_path, cropped_face)

            faces.append({
                "position": self.normalize_face(face),
                "type": "fake" if is_fake(face_path, self.file_th) else "real"
            })
            os.remove(face_path)

        return faces

    def normalize_face(self, face: Sequence[int]) -> list[float]:
        return [
            int(face[0]) / self.width,
            int(face[1]) / self.height,
            int(face[2]) / self.width,
            int(face[3]) / self.height,
        ]

    def draw_rect(self) -> None:
        for (x, y, w, h) in self.faces:
            cv2.rectangle(self.image_array, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow('Detected Faces', self.image_array)
        cv2.waitKey(0)
