from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

# FOTO
POSICAO_FOTO = (154, 278)
DIAMETRO_FOTO = 330

# NOME
POSICAO_NOME_Y = 622
TAMANHO_FONTE_NOME = 42
CAMINHO_FONTE_NOME = str(
    BASE_DIR
    / "fonts"
    / "fonnts.com-Omnium_ExtraBold.otf"
)

# QR CODE
POSICAO_QRCODE = (208, 710)
TAMANHO_QRCODE = 222