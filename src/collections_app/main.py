"""Punto de entrada de la app.

Bootstrap:
1. Parsea `--profile` con argparse (antes de QApplication para fallar
   limpio si el nombre es inválido).
2. Resuelve `db_path` vía `get_db_path_for_profile`.
3. Crea `QApplication` y muestra el splash screen.
4. Para el profile default (sin `--profile`) chequea si existe la DB del
   usuario; si no, copia la semilla del bundle (`_ensure_default_db`).
5. Construye el `AppContext` (aplica migraciones).
6. `_run` abre el `MainWindow`, cierra el splash y corre el event loop.

Uso:
    python -m collections_app.main                  # default profile
    python -m collections_app.main --profile demo   # collections_demo.db
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from collections.abc import Sequence
from pathlib import Path

from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.utils.paths import (
    get_db_path_for_profile,
    get_seed_dir,
)
from collections_app.views.main_window import MainWindow
from collections_app.views.shared.splash import AppSplashScreen
from collections_app.views.shared.theme import apply_app_style

logger = logging.getLogger(__name__)

# Nombre del archivo de DB semilla. Mismo en el bundle (montado en
# `<_MEIPASS>/collections_app/seed/`) y en `<repo>/assets/`.
_SEED_DB_FILENAME = "collections_seed.db"


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="collections_app",
        description=(
            "Collections — gestor de colecciones de cards/cromos. "
            "Sin --profile usa la DB default; con --profile <nombre> "
            "usa collections_<nombre>.db en el mismo directorio."
        ),
    )
    parser.add_argument(
        "--profile",
        default=None,
        help=(
            "Nombre de profile (alfanumerico + guion bajo). "
            "Cada profile es una DB independiente."
        ),
    )
    return parser.parse_args(argv)


def _title_suffix_for(profile: str | None) -> str:
    return f" — [{profile}]" if profile else ""


def _ensure_default_db(db_path: Path) -> None:
    """Si no existe la DB del usuario, copia la semilla del bundle.

    Solo aplica al profile default. La semilla se busca en dos
    ubicaciones (en orden):

    1. `<_MEIPASS>/collections_app/seed/collections_seed.db` (bundle).
    2. `<repo>/assets/collections_seed.db` (corriendo desde fuente).

    Si ninguna existe, no copia nada y deja que el migrador cree una
    DB vacía como antes — degradación graceful para entornos de
    desarrollo / CI sin asset generado.
    """
    if db_path.exists():
        return

    repo_seed = Path(__file__).resolve().parent.parent.parent / "assets" / _SEED_DB_FILENAME
    candidates = [get_seed_dir() / _SEED_DB_FILENAME, repo_seed]
    for seed in candidates:
        if seed.is_file():
            shutil.copy2(seed, db_path)
            logger.info("DB semilla copiada de %s a %s", seed, db_path)
            return
    logger.info(
        "No se encontro DB semilla (chequeado: %s). Se creara DB vacia.",
        ", ".join(str(c) for c in candidates),
    )


def _run(
    ctx: AppContext,
    app: QApplication,
    profile: str | None,
    *,
    splash: AppSplashScreen | None = None,
) -> int:
    """Crea el `MainWindow`, cierra el splash y corre el event loop.

    `splash` es keyword-only y opcional: los tests del bootstrap mockean
    esta función con `def fake_run(ctx, app, profile, **_kwargs)` y no
    necesitan saber del splash. En producción `main()` lo pasa siempre.
    """
    window = MainWindow(ctx=ctx, title_suffix=_title_suffix_for(profile))
    if splash is not None:
        splash.set_progress(90)
    # Prompt 6: arrancar maximizado para que la app aproveche la
    # pantalla completa sin que el usuario tenga que redimensionar.
    # El `resize(1024, 720)` interno del MainWindow sigue siendo el
    # tamaño "restored" si el usuario desmaximiza.
    window.showMaximized()
    if splash is not None:
        splash.set_progress(100)
        splash.finish(window)
    return app.exec()


def main(argv: Sequence[str] | None = None) -> int:
    """Entrypoint del script.

    Returns:
        0 al cerrar la app.
        2 si --profile es inválido (mensaje al usuario via stderr).
    """
    args = _parse_args(argv)
    try:
        db_path = get_db_path_for_profile(args.profile)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    app = QApplication.instance() or QApplication(sys.argv)
    apply_app_style(app)

    splash = AppSplashScreen()
    splash.show()
    QApplication.processEvents()

    # Solo aplicar la semilla al profile default (sin --profile). Los
    # profiles nombrados (demo, mundial, etc.) tienen su propia DB y
    # nunca se "semilan" automáticamente.
    if args.profile is None:
        _ensure_default_db(db_path)
    splash.set_progress(20)

    ctx = create_app_context(db_path)
    splash.set_progress(60)
    try:
        return _run(ctx, app, args.profile, splash=splash)
    finally:
        ctx.close()


if __name__ == "__main__":
    sys.exit(main())
