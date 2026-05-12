"""Compila CollectionsApp.exe con PyInstaller (Windows x64, onefile).

Uso:
    python build/build_app.py
    python build/build_app.py --clean   # borrar dist/ y build/work/ antes
    python build/build_app.py --debug   # consola visible para diagnóstico

El resultado es `dist/CollectionsApp.exe` standalone (~150-250 MB con
PySide6 + reportlab + Pillow incluidos; sin torch/easyocr/ultralytics —
esos se instalan bajo demanda desde la app). En el primer arranque
tarda 5-15s extrayendo a %TEMP% — comportamiento normal de onefile.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SPEC = ROOT / "build" / "collections-app.spec"
DIST = ROOT / "dist"
WORK = ROOT / "build" / "work"
EXE = DIST / "CollectionsApp.exe"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build collections-client.exe")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Borrar dist/ y build/work/ antes de compilar",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Compilar con consola visible para ver tracebacks de runtime",
    )
    args = parser.parse_args(argv)

    if args.clean:
        for path in (DIST, WORK):
            if path.exists():
                print(f"Limpiando {path}…")
                shutil.rmtree(path)

    cmd: list[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--distpath",
        str(DIST),
        "--workpath",
        str(WORK),
        "--noconfirm",
    ]
    if args.debug:
        # `--log-level DEBUG` SÍ es compatible con un .spec (a diferencia
        # de `--debug all` que solo aplica cuando PyInstaller genera el
        # spec desde cero). Muestra el grafo de imports y warnings que
        # ayudan a diagnosticar módulos faltantes.
        # Para consola visible en runtime y prints de bootloader, hay que
        # editar `build/collections-client.spec` (poner `console=True` y
        # agregar `bootloader_ignore_signals` etc.) — flags CLI no llegan
        # cuando el .spec ya define el EXE.
        print("MODO DEBUG: --log-level DEBUG (más logs de PyInstaller)")
        cmd += ["--log-level", "DEBUG"]

    cmd.append(str(SPEC))

    print(f"\nComando: {' '.join(cmd)}\n")
    # ruff S603: subprocess con comando construido programáticamente.
    # El comando solo contiene rutas y flags conocidos (no input externo).
    result = subprocess.run(cmd, cwd=ROOT, check=False)  # noqa: S603

    if result.returncode != 0:
        print("\nERROR: compilación fallida.")
        print("Tip: correr con --debug para ver más detalles.")
        return 1

    if not EXE.exists():
        print(f"\nERROR: el .exe no aparece en {EXE}")
        return 1

    size_mb = EXE.stat().st_size / 1_048_576
    # Sin Unicode no-ASCII en stdout: la consola Windows default
    # (cp1252) explota con caracteres como check marks.
    print("\n[OK] Compilacion exitosa")
    print(f"  Archivo: {EXE}")
    print(f"  Tamano:  {size_mb:.1f} MB")
    print(f"\nPara distribuir: copiar solo {EXE.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
