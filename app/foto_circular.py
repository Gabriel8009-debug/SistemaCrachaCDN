from pathlib import Path
import tempfile

from PIL import Image, ImageDraw

from app.face_cropper import FaceCropper


cropper = FaceCropper()


def criar_foto_circular(caminho_foto, caminho_saida, diametro):

    with tempfile.NamedTemporaryFile(
        suffix=".png",
        delete=False
    ) as arquivo_temp:

        caminho_temp = Path(arquivo_temp.name)

    # Centraliza automaticamente o rosto
    cropper.centralizar(
        entrada=caminho_foto,
        saida=caminho_temp
    )

    foto = Image.open(caminho_temp).convert("RGBA")

    foto = foto.resize(
        (diametro, diametro),
        Image.Resampling.LANCZOS
    )

    mascara = Image.new(
        "L",
        (diametro, diametro),
        0
    )

    desenho = ImageDraw.Draw(mascara)

    desenho.ellipse(
        (0, 0, diametro, diametro),
        fill=255
    )

    foto.putalpha(mascara)

    foto.save(caminho_saida)

    caminho_temp.unlink(missing_ok=True)

    print("Foto circular criada!")