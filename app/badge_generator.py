from PIL import Image, ImageDraw, ImageFont

from . import config
from .qrcode_service import gerar_qrcode_whatsapp


PREPOSICOES_NOME = {
    "da",
    "de",
    "do",
    "das",
    "dos",
    "e",
}


def padronizar_nome(nome: str) -> str:
    """
    Padroniza o nome para o formato:
    Michelle Morabito
    Maria da Silva
    João dos Santos
    """

    palavras = str(nome).strip().lower().split()

    if not palavras:
        return ""

    nome_formatado = []

    for indice, palavra in enumerate(palavras):

        if indice > 0 and palavra in PREPOSICOES_NOME:
            nome_formatado.append(palavra)
        else:
            nome_formatado.append(palavra.capitalize())

    return " ".join(nome_formatado)


def gerar_cracha_corretor(
    template_path: str,
    foto_path: str,
    saida_path: str,
    nome: str,
    telefone: str,
    mensagem_whatsapp: str,
) -> None:

    template = Image.open(template_path).convert("RGBA")
    foto = Image.open(foto_path).convert("RGBA")

    template.paste(
        foto,
        config.POSICAO_FOTO,
        foto,
    )

    draw = ImageDraw.Draw(template)

    # ============================
    # FONTE
    # ============================

    caminho_fonte = str(config.CAMINHO_FONTE_NOME).strip()

    print("\n==============================")
    print("Fonte carregada de:")
    print(caminho_fonte)
    print("==============================\n")

    fonte = ImageFont.truetype(
        caminho_fonte,
        config.TAMANHO_FONTE_NOME,
    )

    # ============================
    # NOME
    # ============================

    nome = padronizar_nome(nome)

    caixa_texto = draw.textbbox(
        (0, 0),
        nome,
        font=fonte,
    )

    largura_texto = caixa_texto[2] - caixa_texto[0]

    x_nome = (
        template.width - largura_texto
    ) / 2

    draw.text(
        (
            x_nome,
            config.POSICAO_NOME_Y,
        ),
        nome,
        font=fonte,
        fill="black",
    )

    # ============================
    # QR CODE
    # ============================

    qr = gerar_qrcode_whatsapp(
        telefone,
        mensagem_whatsapp,
        config.TAMANHO_QRCODE,
    )

    template.paste(
        qr,
        config.POSICAO_QRCODE,
    )

    template.save(saida_path)

    print(f"Crachá salvo em: {saida_path}")