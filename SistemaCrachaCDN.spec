# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

ROOT = Path(SPECPATH)

datas = []
binaries = []

# Dados efetivamente necessários em tempo de execução.
for pacote in ("customtkinter", "mediapipe", "rapidocr"):
    try:
        datas += collect_data_files(pacote)
    except Exception:
        pass

try:
    binaries += collect_dynamic_libs("onnxruntime")
except Exception:
    pass

for pasta in ("templates", "fonts", "models", "app/ui/assets", "config"):
    caminho = ROOT / pasta
    if caminho.exists():
        datas.append((str(caminho), pasta.replace("\\", "/")))

hiddenimports = [
    "win32api", "win32con", "win32event", "win32print", "win32ui",
    "pywintypes", "pythoncom",
    "googleapiclient.discovery", "googleapiclient.http",
    "google.oauth2.service_account",
    "app.vision", "app.vision.capture", "app.vision.ocr_engine",
    "app.vision.parsers", "app.vision.preprocess", "app.vision.reader",
    "app.vision.regions",
]

excludes = [
    "tkinter.test", "unittest", "pytest",
    "mediapipe.tasks.python.test", "mediapipe.tasks.python.benchmark",
    "mediapipe.tasks.python.genai", "onnxruntime.quantization",
    "onnxruntime.transformers", "onnxruntime.tools",
    "win32com.test", "win32com.demos",
    "qrcode.tests", "PIL.report",
]

a = Analysis(
    ["main.py"],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="SistemaCrachaCDN",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory="_internal",
    icon="icone_cdn.ico",
    version="version_info.txt",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="SistemaCrachaCDN",
)
