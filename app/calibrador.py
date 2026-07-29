from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def criar_calibrador(
    imagem_referencia: str,
    caminho_saida: str,
    intervalo: int = 50,
) -> None:
    referencia = Path(imagem_referencia)
    saida = Path(caminho_saida)

    if not referencia.exists():
        raise FileNotFoundError(
            f"Imagem de referência não encontrada: {referencia}"
        )

    saida.parent.mkdir(parents=True, exist_ok=True)

    imagem = Image.open(referencia).convert("RGBA")
    desenho = ImageDraw.Draw(imagem)

    fonte = ImageFont.truetype(
        "C:/Windows/Fonts/arial.ttf",
        14,
    )

    for x in range(0, imagem.width, intervalo):
        desenho.line(
            (x, 0, x, imagem.height),
            fill="#D0D0D0",
            width=1,
        )

        desenho.text(
            (x + 3, 3),
            str(x),
            fill="#FF0000",
            font=fonte,
        )

    for y in range(0, imagem.height, intervalo):
        desenho.line(
            (0, y, imagem.width, y),
            fill="#D0D0D0",
            width=1,
        )

        desenho.text(
            (3, y + 3),
            str(y),
            fill="#FF0000",
            font=fonte,
        )

    imagem.save(saida)

    print(f"Calibrador criado: {saida.resolve()}")


if __name__ == "__main__":
    criar_calibrador(
        imagem_referencia="templates/referencia_corretor.png",
        caminho_saida="output/calibrador_referencia_corretor.png",
        intervalo=50,
    )