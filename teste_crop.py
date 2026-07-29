from pathlib import Path

from app.face_cropper import FaceCropper

BASE_DIR = Path(__file__).resolve().parent

entrada = BASE_DIR / "fotos_temp" / "foto_linha_348.jpg"
saida = BASE_DIR / "fotos_temp" / "foto_centralizada.png"

cropper = FaceCropper()

cropper.centralizar(
    entrada=entrada,
    saida=saida
)

print("Foto centralizada criada com sucesso!")