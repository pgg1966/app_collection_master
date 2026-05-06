"""Punto de entrada de la app.

Bootstrap:
1. Parsea `--profile` con argparse (antes de QApplication para fallar
   limpio si el nombre es inválido).
2. Resuelve `db_path` vía `get_db_path_for_profile`.
3. Construye el `AppContext` (aplica migraciones).
4. Abre `MainWindow` con el sufijo de título correspondiente.
5. Corre el event loop hasta cierre.

Uso:
    python -m collections_app.main                  # default profile
    python -m collections_app.main --profile demo   # collections_demo.db
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.utils.paths import get_db_path_for_profile
from collections_app.views.main_window import MainWindow
from collections_app.views.shared.theme import apply_app_style


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


def _run(ctx: AppContext, app: QApplication, profile: str | None) -> int:
    """Ejecuta la app con `ctx` ya construido. Separado del `main()` para
    que sea testeable inyectando un context contra `:memory:`."""
    window = MainWindow(ctx=ctx, title_suffix=_title_suffix_for(profile))
    window.show()
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
    ctx = create_app_context(db_path)
    try:
        return _run(ctx, app, args.profile)
    finally:
        ctx.close()


if __name__ == "__main__":
    sys.exit(main())
