from pathlib import Path
import importlib
import json
import sys

ROOT = Path(__file__).resolve().parent
ERROS = []

RECURSOS = [
    "main.py", "SistemaCrachaCDN.spec", "icone_cdn.ico", "version_info.txt",
    "templates/corretor.png", "templates/supervisor_base.png",
    "fonts/fonnts.com-Omnium_ExtraBold.otf", "fonts/RobotoCondensed-Regular.ttf",
    "models/blaze_face_short_range.tflite",
    "config/supervisor_layout.json", "config/sisweb_coordenadas.json",
    "config/sisweb_regioes.json",
]

for rel in RECURSOS:
    if not (ROOT / rel).exists():
        ERROS.append(f"Arquivo ausente: {rel}")

for rel in ("config/supervisor_layout.json", "config/sisweb_coordenadas.json", "config/sisweb_regioes.json"):
    try:
        json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        ERROS.append(f"JSON inválido em {rel}: {exc}")

for modulo in (
    "customtkinter", "PIL", "qrcode", "cv2", "mediapipe",
    "googleapiclient", "google.oauth2", "win32print", "rapidocr",
    "onnxruntime", "pyautogui", "pyperclip", "pywinauto",
):
    try:
        importlib.import_module(modulo)
    except Exception as exc:
        ERROS.append(f"Dependência/import falhou: {modulo}: {exc}")

if ERROS:
    print("VALIDAÇÃO REPROVADA")
    for erro in ERROS:
        print("-", erro)
    sys.exit(1)

print("VALIDAÇÃO APROVADA")
print("Recursos e dependências essenciais disponíveis para o build.")
