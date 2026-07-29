from pathlib import Path

from app.face_detector import DetectorFace


BASE_DIR = Path(__file__).resolve().parent

CAMINHO_FOTO = (
    BASE_DIR
    / "fotos_temp"
    / "foto_linha_348.jpg"
)


if not CAMINHO_FOTO.exists():
    raise FileNotFoundError(
        f"Foto de teste não encontrada: {CAMINHO_FOTO}"
    )


detector = DetectorFace()

resultado = detector.detectar(
    CAMINHO_FOTO
)

quantidade_rostos = len(resultado.detections)

print()
print(f"Rostos encontrados: {quantidade_rostos}")
print()

for indice, deteccao in enumerate(
    resultado.detections,
    start=1,
):
    caixa = deteccao.bounding_box

    print(f"Rosto {indice}")
    print(f"X: {caixa.origin_x}")
    print(f"Y: {caixa.origin_y}")
    print(f"Largura: {caixa.width}")
    print(f"Altura: {caixa.height}")
    print("-" * 40)