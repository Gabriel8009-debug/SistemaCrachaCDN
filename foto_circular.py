from PIL import Image, ImageDraw, ImageOps


def criar_foto_circular(
    caminho_foto: str,
    caminho_saida: str,
    diametro: int,
) -> None:
    foto = Image.open(caminho_foto).convert("RGBA")

    tamanho = (diametro, diametro)

    foto = ImageOps.fit(
        foto,
        tamanho,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.4),
    )

    mascara = Image.new("L", tamanho, 0)
    desenho = ImageDraw.Draw(mascara)

    desenho.ellipse(
        (0, 0, diametro - 1, diametro - 1),
        fill=255,
    )

    foto.putalpha(mascara)
    foto.save(caminho_saida)

    print(f"Foto circular criada: {caminho_saida}")