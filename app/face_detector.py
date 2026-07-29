from pathlib import Path

import cv2
import mediapipe as mp

from app.path_manager import MODELS


MODELO_FACE = MODELS / "blaze_face_short_range.tflite"


class DetectorFace:

    def __init__(self):

        BaseOptions = mp.tasks.BaseOptions
        FaceDetector = mp.tasks.vision.FaceDetector
        FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = FaceDetectorOptions(
            base_options=BaseOptions(
                model_asset_path=str(MODELO_FACE)
            ),
            running_mode=VisionRunningMode.IMAGE,
            min_detection_confidence=0.60,
        )

        self.detector = FaceDetector.create_from_options(
            options
        )

    def detectar(self, caminho_imagem):

        imagem = cv2.imread(str(caminho_imagem))

        imagem_rgb = cv2.cvtColor(
            imagem,
            cv2.COLOR_BGR2RGB,
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=imagem_rgb,
        )

        resultado = self.detector.detect(
            mp_image
        )

        return resultado