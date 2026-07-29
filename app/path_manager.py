from pathlib import Path
import sys

# Recursos empacotados pelo PyInstaller ficam em sys._MEIPASS.
# Dados mutáveis permanecem ao lado do executável.
if getattr(sys, "frozen", False):
    RESOURCE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    DATA_DIR = Path(sys.executable).resolve().parent
else:
    RESOURCE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = RESOURCE_DIR

BASE_DIR = DATA_DIR
CREDENTIALS = DATA_DIR / "credentials"
OUTPUT = DATA_DIR / "output"
LOGS = DATA_DIR / "logs"
FOTOS_TEMP = DATA_DIR / "fotos_temp"

FONTS = RESOURCE_DIR / "fonts"
MODELS = RESOURCE_DIR / "models"
TEMPLATES = RESOURCE_DIR / "templates"
CONFIG = RESOURCE_DIR / "config"


def garantir_diretorios() -> None:
    """Cria os diretórios mutáveis usados pela aplicação."""
    for diretorio in (CREDENTIALS, OUTPUT, LOGS, FOTOS_TEMP):
        diretorio.mkdir(parents=True, exist_ok=True)


garantir_diretorios()
