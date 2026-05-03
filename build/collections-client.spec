# -*- mode: python ; coding: utf-8 -*-
# Spec PyInstaller para collections-client.exe (Windows x64, onefile).
#
# Compilar con:
#     python build/build_client.py [--clean] [--debug]
#
# El .spec se modifica como código Python: PyInstaller lo ejecuta y usa
# los objetos resultantes (Analysis / PYZ / EXE) para empaquetar.

from pathlib import Path

ROOT = Path(SPECPATH).parent
SRC = ROOT / "src"

block_cipher = None

a = Analysis(
    [str(SRC / "collections_app" / "client" / "main.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=[
        # Migraciones SQL — imprescindibles en runtime para inicializar la DB.
        # Se montan en _MEIPASS/collections_app/core/db/schema (ver
        # `_get_bundle_dir()` en paths.py).
        (
            str(SRC / "collections_app" / "core" / "db" / "schema"),
            "collections_app/core/db/schema",
        ),
    ],
    hiddenimports=[
        # Repositorios — algunos se importan de forma indirecta y PyInstaller
        # no detecta el grafo si no se enumeran.
        "collections_app.core.db.migrator",
        "collections_app.core.repositories.settings_repo",
        "collections_app.core.repositories.collections_repo",
        "collections_app.core.repositories.codes_headers_repo",
        "collections_app.core.repositories.codes_lines_repo",
        "collections_app.core.repositories.cards_repo",
        "collections_app.core.repositories.inventory_repo",
        "collections_app.core.repositories.transactions_repo",
        "collections_app.core.repositories.card_images_repo",
        # Servicios
        "collections_app.core.services.album_service",
        "collections_app.core.services.pdf_generator",
        "collections_app.core.services.inventory_service",
        "collections_app.core.services.license_service",
        "collections_app.core.services.reports_service",
        "collections_app.core.services.collections_service",
        "collections_app.core.services.settings_service",
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
        # El cliente NO necesita el código de admin ni sus deps de scraping.
        "collections_app.admin",
        "cv2",
        "duckduckgo_search",
        "bs4",
        # Stdlib pesado que la app cliente no usa.
        "tkinter",
        "unittest",
        "email",
        "xml.etree",
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
    name="collections-client",
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
