from urllib.parse import quote

import qrcode
from PIL import Image


def gerar_qrcode_whatsapp(
    telefone: str,
    mensagem: str,
    tamanho: int,
) -> Image.Image:
    telefone_limpo = "".join(
        caractere
        for caractere in telefone
        if caractere.isdigit()
    )

    mensagem_codificada = quote(mensagem)

    link = (
        f"https://wa.me/{telefone_limpo}"
        f"?text={mensagem_codificada}"
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )

    qr.add_data(link)
    qr.make(fit=True)

    imagem_qr = qr.make_image(
        fill_color="black",
        back_color="white",
    ).convert("RGBA")

    return imagem_qr.resize(
        (tamanho, tamanho),
        Image.Resampling.NEAREST,
    )