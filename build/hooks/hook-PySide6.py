"""Hook PyInstaller para PySide6 — recolecta plugins Qt necesarios en Windows.

Sin este hook, el .exe arranca y muere con:
    "This application failed to start because no Qt platform plugin
     could be initialized..."

Los plugins de Qt son DLLs separadas que viven en
`PySide6/plugins/<categoría>/`. PyInstaller no las detecta a menos que
las pidamos explícitamente.

Categorías incluidas:
- platforms — backend de ventanas (qwindows.dll en Windows). Imprescindible.
- imageformats — JPG/PNG/WebP/SVG via QImageReader.
- styles — Fusion, Windows, etc. para QApplication.setStyle.
- iconengines — soporte de íconos SVG vía QIcon.
"""

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

datas = collect_data_files(
    "PySide6",
    includes=[
        "plugins/platforms/*",
        "plugins/imageformats/*",
        "plugins/styles/*",
        "plugins/iconengines/*",
    ],
)
binaries = collect_dynamic_libs("PySide6")
