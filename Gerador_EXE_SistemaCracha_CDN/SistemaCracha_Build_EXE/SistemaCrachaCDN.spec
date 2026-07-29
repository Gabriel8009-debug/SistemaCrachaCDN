# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

ROOT = Path(SPECPATH)

datas = []
hiddenimports = []
binaries = []

def add_collect(package_name):
    global datas, hiddenimports, binaries
    try:
        d, b, h = collect_all(package_name)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

for pacote in [
    "customtkinter",
    "mediapipe",
    "cv2",
    "PIL",
    "qrcode",
    "google",
    "googleapiclient",
    "google_auth_httplib2",
    "google.oauth2",
    "win32com",
]:
    add_collect(pacote)

# Pastas que precisam acompanhar a aplicação
for pasta in [
    "templates",
    "fonts",
    "models",
    "app/ui/assets",
]:
    caminho = ROOT / pasta
    if caminho.exists():
        datas.append((str(caminho), pasta.replace("\\", "/")))

# Arquivos adicionais opcionais
for arquivo in [
    "config.json",
]:
    caminho = ROOT / arquivo
    if caminho.exists():
        datas.append((str(caminho), "."))

a = Analysis(
    ["main.py"],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + [
        "win32print",
        "win32api",
        "win32event",
        "win32con",
        "pywintypes",
        "pythoncom",
        "googleapiclient.discovery",
        "googleapiclient.http",
        "google.oauth2.service_account",
        "mediapipe.python.solutions.face_detection",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter.test",
        "unittest",
        "pydoc",
    ],
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
