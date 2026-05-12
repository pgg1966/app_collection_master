# -*- mode: python ; coding: utf-8 -*-
# Spec PyInstaller para CollectionsApp.exe (Windows x64, onefile).
#
# Compilar con:
#     python build/build_app.py [--clean] [--debug]
#
# El .spec se modifica como código Python: PyInstaller lo ejecuta y usa
# los objetos resultantes (Analysis / PYZ / EXE) para empaquetar.
#
# Bundle "liviano": las dependencias pesadas del OCR (torch, torchvision,
# ultralytics, easyocr, cv2) NO van adentro — se instalan bajo demanda
# desde la app (OcrInstallService) la primera vez que el usuario abre
# la tab "Por foto". Ver docs/install_guide.md.

from pathlib import Path

ROOT = Path(SPECPATH).parent
SRC = ROOT / "src"
ASSETS = ROOT / "assets"

block_cipher = None

# Datas estáticos del bundle. La DB semilla se agrega condicionalmente
# (si existe en assets/) para que el build no falle en entornos sin
# generarla — la app degrada graceful a "DB vacía" si la semilla no
# está, ver `_ensure_default_db` en main.py.
_datas = [
    # Migraciones SQL — imprescindibles en runtime para inicializar la DB.
    # Se montan en _MEIPASS/collections_app/core/db/schema (ver
    # `_get_bundle_dir()` en paths.py).
    (
        str(SRC / "collections_app" / "core" / "db" / "schema"),
        "collections_app/core/db/schema",
    ),
]

_seed_db = ASSETS / "collections_seed.db"
if _seed_db.is_file():
    # Montado en _MEIPASS/collections_app/seed/ (ver `get_seed_dir()` en
    # paths.py). Si la semilla no existe en assets/, el build sigue y la
    # app arranca con DB vacía.
    _datas.append((str(_seed_db), "collections_app/seed"))

a = Analysis(
    [str(SRC / "collections_app" / "main.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=_datas,
    hiddenimports=[
        # core/db
        "collections_app.core.db.migrator",
        "collections_app.core.db.connection",
        # core/repositories
        "collections_app.core.repositories.app_settings_repo",
        "collections_app.core.repositories.collections_repo",
        "collections_app.core.repositories.code_headers_repo",
        "collections_app.core.repositories.code_lines_repo",
        "collections_app.core.repositories.cards_repo",
        "collections_app.core.repositories.inventory_repo",
        "collections_app.core.repositories.transactions_repo",
        "collections_app.core.repositories.card_images_repo",
        # services — todos los que el AppContext instancia o expone vía factory
        "collections_app.services.settings_service",
        "collections_app.services.collections_service",
        "collections_app.services.code_headers_service",
        "collections_app.services.code_lines_service",
        "collections_app.services.cards_service",
        "collections_app.services.transactions_service",
        "collections_app.services.inventory_service",
        "collections_app.services.csv_import_service",
        "collections_app.services.inventory_import_service",
        "collections_app.services.inventory_snapshot_service",
        "collections_app.services.matching_service",
        "collections_app.services.exchange_import_service",
        "collections_app.services.exchange_export_service",
        "collections_app.services.exchange_apply_service",
        "collections_app.services.exchange_errors",
        "collections_app.services.exceptions",
        # OCR — los modulos .py de la app SI van (son chicos y se importan
        # de forma indirecta via app_context.get_ocr_service). Los packages
        # pesados que ellos consumen (torch/cv2/etc.) estan en `excludes`.
        "collections_app.services.ocr_install_service",
        "collections_app.services.ocr_service",
        "collections_app.services.ocr_reader",
        "collections_app.services.ocr_validator",
        # PySide6 — módulos que pueden no detectarse si la app los usa
        # solo de forma indirecta (ej. SVG en QPixmap, print preview).
        "PySide6.QtSvg",
        "PySide6.QtXml",
        "PySide6.QtPrintSupport",
        # Pillow — formatos de imagen usados al renderear cards/escudos.
        "PIL.JpegImagePlugin",
        "PIL.PngImagePlugin",
        "PIL.WebPImagePlugin",
        # reportlab — barcode submódulos no se importan transitivamente.
        "reportlab.graphics.barcode",
        "reportlab.graphics.barcode.code128",
        "reportlab.rl_config",
        # pypdf — para validate_exchange_pdf_metadata.
        "pypdf",
        "pypdf._reader",
        "pypdf._writer",
        "pypdf.generic",
    ],
    hookspath=["build/hooks"],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Dependencias pesadas del OCR — NO van en el bundle, se instalan
        # bajo demanda (OcrInstallService). Mantener el .exe liviano.
        "torch",
        "torchvision",
        "ultralytics",
        "easyocr",
        "cv2",
        # Scraping y similares — no se usan en la app cliente.
        "duckduckgo_search",
        "bs4",
        # Stdlib pesado que la app no usa.
        # OJO: NO excluir `email`, `xml.etree` ni `urllib` — reportlab los
        # arrastra transitivamente (reportlab/lib/utils.py → urllib.request
        # → email). Excluirlos rompe el .exe en runtime con
        # "No module named 'email'".
        "tkinter",
        "unittest",
        "pydoc",
        "doctest",
    ],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="CollectionsApp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX puede romper PySide6 (DLLs Qt firmadas) → desactivado a propósito.
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    # console=False → sin ventana negra. Cambiar a True si --debug en CLI.
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="build/icon.ico",  # TODO: agregar cuando haya ícono.
)

# TODO splash screen: requiere build/splash.png (400x200). Ejemplo:
#     splash = Splash(str(ROOT / "build" / "splash.png"), ...)
#     EXE(..., splash, splash.binaries, ...)
# Mejora UX el primer arranque (5-15s mientras se extrae a %TEMP%).
