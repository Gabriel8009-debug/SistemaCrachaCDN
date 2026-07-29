from PIL import Image, ImageDraw, ImageFont

from . import config
from .qrcode_service import gerar_qrcode_whatsapp


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

    fonte = ImageFont.truetype(
    config.CAMINHO_FONTE_NOME,
    config.TAMANHO_FONTE_NOME,
)

    caixa_texto = draw.textbbox(
        (0, 0),
        nome,
        font=fonte,
    )

    largura_texto = caixa_texto[2] - caixa_texto[0]
    x_nome = (template.width - largura_texto) // 2

    draw.text(
        (x_nome, config.POSICAO_NOME_Y),
        nome,
        fill="#000000",
        font=fonte,
    )

    qr_code = gerar_qrcode_whatsapp(
        telefone=telefone,
        mensagem=mensagem_whatsapp,
        tamanho=config.TAMANHO_QRCODE,
    )

    template.paste(
        qr_code,
        config.POSICAO_QRCODE,
        qr_code,
    )

    template.save(saida_path)

    print(f"Crachá criado com sucesso: {saida_path}")