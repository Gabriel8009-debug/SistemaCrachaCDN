from pathlib import Path

import win32con
import win32print
import win32ui
from PIL import Image, ImageWin


NOME_IMPRESSORA = "IDP CUBO1 Card Printer"

CAMINHO_IMAGEM = Path(
    r"C:\SistemaCracha\output\2026-07-24"
    r"\cracha_361_michelle_morabito.png"
)


def imprimir_imagem(
    caminho_imagem: Path,
    nome_impressora: str,
) -> None:

    if not caminho_imagem.exists():
        raise FileNotFoundError(
            f"Imagem não encontrada: {caminho_imagem}"
        )

    impressoras = [
        impressora[2]
        for impressora in win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL
            | win32print.PRINTER_ENUM_CONNECTIONS
        )
    ]

    if nome_impressora not in impressoras:
        raise RuntimeError(
            f'Impressora não encontrada: "{nome_impressora}"'
        )

    imagem = Image.open(caminho_imagem).convert("RGB")

    # O driver da Cubo1 trabalha com a área física em paisagem.
    # A arte vertical é girada somente no momento da impressão.
    if imagem.height > imagem.width:
        imagem = imagem.rotate(
            90,
            expand=True,
        )

    dc = win32ui.CreateDC()
    dc.CreatePrinterDC(nome_impressora)

    largura_imprimivel = dc.GetDeviceCaps(
        win32con.HORZRES
    )

    altura_imprimivel = dc.GetDeviceCaps(
        win32con.VERTRES
    )

    largura_imagem, altura_imagem = imagem.size

    escala = min(
        largura_imprimivel / largura_imagem,
        altura_imprimivel / altura_imagem,
    )

    largura_final = int(
        largura_imagem * escala
    )

    altura_final = int(
        altura_imagem * escala
    )

    x = int(
        (largura_imprimivel - largura_final) / 2
    )

    y = int(
        (altura_imprimivel - altura_final) / 2
    )

    print(f"Impressora: {nome_impressora}")
    print(
        f"Área imprimível: "
        f"{largura_imprimivel} x {altura_imprimivel}"
    )
    print(
        f"Imagem após rotação: "
        f"{largura_imagem} x {altura_imagem}"
    )
    print(
        f"Imagem enviada: "
        f"{largura_final} x {altura_final}"
    )

    dc.StartDoc("Teste de crachá Cubo1")
    dc.StartPage()

    dib = ImageWin.Dib(imagem)

    dib.draw(
        dc.GetHandleOutput(),
        (
            x,
            y,
            x + largura_final,
            y + altura_final,
        ),
    )

    dc.EndPage()
    dc.EndDoc()
    dc.DeleteDC()

    print("Arquivo enviado para a fila de impressão.")


if __name__ == "__main__":

    resposta = input(
        "Este teste enviará 1 crachá para a Cubo1. "
        "Continuar? [S/N]: "
    ).strip().lower()

    if resposta != "s":
        print("Impressão cancelada.")
    else:
        imprimir_imagem(
            CAMINHO_IMAGEM,
            NOME_IMPRESSORA,
        )