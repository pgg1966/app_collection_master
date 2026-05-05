"""Punto de entrada de la app.

Bootstrap mínimo: arma el `AppContext`, abre la vista preservada
`CardLoaderView` con la primera colección disponible, y corre el
event loop. Si no hay colecciones cargadas, muestra un dialog
informativo y sale con código 0.

Está pensado como spike funcional para validar el stack end-to-end.
La nav real (selector de colecciones, menú principal, etc.) la arma
Prompt 3.

Uso:
    python -m collections_app.main
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.utils.paths import get_default_db_path
from collections_app.views.inventory.card_loader import CardLoaderView
from collections_app.views.shared.theme import apply_app_style


def _run(ctx: AppContext, app: QApplication) -> int:
    """Resuelve la colección activa y lanza la vista preservada.

    Se separa del `main()` para que sea testeable con un AppContext
    inyectado contra `:memory:`.
    """
    collections = ctx.collections.list_all()
    if not collections:
        QMessageBox.information(
            None,
            "Collections",
            "No hay colecciones cargadas. La carga inicial se hara en Prompt 3.",
        )
        return 0
    view = CardLoaderView(service=ctx.inventory, collection=collections[0])
    view.setWindowTitle("Collections — Carga rapida")
    view.show()
    return app.exec()


def main() -> int:
    app = QApplication(sys.argv)
    apply_app_style(app)
    ctx = create_app_context(get_default_db_path())
    try:
        return _run(ctx, app)
    finally:
        ctx.close()


if __name__ == "__main__":
    sys.exit(main())
