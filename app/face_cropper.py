from pathlib import Path

import cv2

from app.face_detector import DetectorFace


class FaceCropper:

    def __init__(self):
        self.detector = DetectorFace()

    def centralizar(self, entrada, saida):

        resultado = self.detector.detectar(entrada)

        if len(resultado.detections) != 1:
            raise Exception("Não foi possível localizar exatamente um rosto.")

        imagem = cv2.imread(str(entrada))

        h, w = imagem.shape[:2]

        caixa = resultado.detections[0].bounding_box

        centro_x = caixa.origin_x + caixa.width / 2
        centro_y = caixa.origin_y + caixa.height / 2

        tamanho = int(max(caixa.width, caixa.height) * 2.2)

        x1 = int(centro_x - tamanho / 2)
        y1 = int(centro_y - tamanho / 2)

        x2 = x1 + tamanho
        y2 = y1 + tamanho

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)

        recorte = imagem[y1:y2, x1:x2]

        recorte = cv2.resize(
            recorte,
            (800, 800),
            interpolation=cv2.INTER_CUBIC
        )

        cv2.imwrite(str(saida), recorte)