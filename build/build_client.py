"""Compila collections-client.exe con PyInstaller (Windows x64, onefile).

Uso:
    python build/build_client.py
    python build/build_client.py --clean   # borrar dist/ y build/work/ antes
    python build/build_client.py --debug   # consola visible para diagnóstico

El resultado es `dist/collections-client.exe` standalone (~80-150 MB con
PySide6 + reportlab + Pillow incluidos). En el primer arranque tarda
5-15s extrayendo a %TEMP% — comportamiento normal de onefile.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SPEC = ROOT / "build" / "collections-client.spec"
DIST = ROOT / "dist"
WORK = ROOT / "build" / "work"
EXE = DIST / "collections-client.exe"


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
        # `--debug all` agrega prints de bootloader; combinado con
        # `console=True` (que el spec respeta solo si modificás manualmente)
        # ayuda a diagnosticar arranque fallido. La consola en sí se queda
        # en False según el spec — para activar consola, editá el spec o
        # corré `--debug imports`.
        print("MODO DEBUG: --debug all (más logs de PyInstaller)")
        cmd += ["--debug", "all"]

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
