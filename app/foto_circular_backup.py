from PIL import Image, ImageDraw, ImageOps


def criar_foto_circular(caminho_foto, caminho_saida, diametro):

    foto = Image.open(caminho_foto).convert("RGBA")

    tamanho = (diametro, diametro)

    foto = ImageOps.fit(
        foto,
        tamanho,
        Image.Resampling.LANCZOS
    )

    mascara = Image.new("L", tamanho, 0)

    desenho = ImageDraw.Draw(mascara)

    desenho.ellipse(
        (0, 0, diametro, diametro),
        fill=255
    )

    foto.putalpha(mascara)

    foto.save(caminho_saida)

    print("Foto circular criada!")


criar_foto_circular(
    "fotos/pessoa.jpg",
    "output/foto_circular.png",
    330
)