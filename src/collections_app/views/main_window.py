"""Ventana principal de la app — orquesta selector + detail view.

Layout:

    +------------------------------------------------+
    | Collections — [profile] (si hay)   File menu   |
    +-------------+----------------------------------+
    |             |                                  |
    | Selector    |  CollectionDetailView (active)   |
    | (sidebar)   |  o EmptyState (sin colecciones)  |
    |             |                                  |
    +-------------+----------------------------------+

QSplitter horizontal con sidebar a la izquierda. El área de contenido
es un `QStackedWidget` que alterna entre el placeholder de empty state
y el `CollectionDetailView` activo.

Cuando el usuario cambia de colección desde el sidebar, el
`CollectionDetailView` activo se **reutiliza**: se propaga la nueva
colección a los 5 tabs vía `set_active_collection`. Destruir + recrear
exhibía un teardown costoso de Qt (~1.3-2s con datasets reales);
reutilizar evita ese costo. Idempotente si la colección seleccionada
es la misma que la activa.

El título refleja el profile activo:
- profile None → "Collections"
- profile != None → "Collections — [<nombre>]"
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.views.admin.cards_abm import CardsAbmView
from collections_app.views.admin.codes_master_detail import CodesMasterDetailView
from collections_app.views.admin.collections_abm import CollectionsAbmView
from collections_app.views.admin.csv_import_dialog import CsvImportDialog
from collections_app.views.collections.collection_detail_view import (
    CollectionDetailView,
)
from collections_app.views.collections.collection_selector import (
    CollectionSelectorView,
)

if TYPE_CHECKING:
    from collections_app.core.models.aggregates.csv_import_report import (
        CsvImportReport,
    )

_EMPTY_STATE_MESSAGE = (
    "No hay colecciones cargadas todavía.\n\n"
    "Cargá una colección desde:\n"
    "  Archivo → Nueva colección desde CSV..."
)


def _make_empty_state_widget() -> QWidget:
    """Placeholder amigable para cuando la DB del profile está sin colecciones."""
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label = QLabel(_EMPTY_STATE_MESSAGE)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setObjectName("emptyStateLabel")
    layout.addWidget(label)
    return widget


class MainWindow(QMainWindow):
    """Punto de entrada visual de la app."""

    def __init__(
        self: MainWindow,
        ctx: AppContext,
        title_suffix: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self.setWindowTitle(f"Collections{title_suffix}")
        self._active_detail: CollectionDetailView | None = None
        self._build_ui()
        self._build_menus()
        self._wire_signals()

        # Carga inicial: si hay >=1 colección, abrir la primera. Si no,
        # mantener el empty state visible.
        if not self._selector.is_empty():
            self._selector.select_first()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self: MainWindow) -> None:
        self._selector = CollectionSelectorView(collections_service=self._ctx.collections)
        self._content_stack = QStackedWidget()
        self._empty_state = _make_empty_state_widget()
        self._content_stack.addWidget(self._empty_state)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._selector)
        splitter.addWidget(self._content_stack)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([260, 740])

        self.setCentralWidget(splitter)
        self.resize(1024, 720)

    def _build_menus(self: MainWindow) -> None:
        """Construye la barra de menús según el modo admin.

        Modo no-admin (Prompt 6): solo aparece "Salir" como acción
        directa en la barra de menús. No hay menú "Archivo" con un
        único item, no hay menú "Administración" con items grises.

        Modo admin (`COLLECTIONS_ADMIN=1`): aparecen "Archivo" (con
        "Nueva colección desde CSV..." + "Salir") y "Administración"
        (Cards, Colecciones, Códigos). Los items admin siempre quedan
        enabled — la rama no-admin no los crea.
        """
        admin_enabled = os.environ.get("COLLECTIONS_ADMIN") == "1"

        if not admin_enabled:
            salir = self.menuBar().addAction(self.tr("&Salir"))
            salir.triggered.connect(self.close)
            return

        archivo = self.menuBar().addMenu(self.tr("&Archivo"))
        nueva = archivo.addAction(self.tr("&Nueva colección desde CSV..."))
        nueva.triggered.connect(self._open_csv_import_dialog)
        archivo.addSeparator()
        salir = archivo.addAction(self.tr("&Salir"))
        salir.triggered.connect(self.close)

        admin = self.menuBar().addMenu(self.tr("A&dministración"))
        cards_action = admin.addAction(self.tr("&Cards..."))
        cards_action.triggered.connect(self._open_cards_abm)
        collections_action = admin.addAction(self.tr("C&olecciones..."))
        collections_action.triggered.connect(self._open_collections_abm)
        codes_action = admin.addAction(self.tr("C&ódigos..."))
        codes_action.triggered.connect(self._open_codes_master_detail)

    def _wire_signals(self: MainWindow) -> None:
        self._selector.collection_selected.connect(self._on_collection_selected)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_collection_selected(self: MainWindow, collection: Collection) -> None:
        """Activa el detail de `collection`, reutilizándolo si ya existe.

        Reutilización (vs destruir+recrear) elimina el costo de teardown
        de los widgets del detail anterior, que era el bottleneck del
        cambio lento (logs del commit `fe24c8d` mostraron que el delay
        venía de la destrucción, no de la construcción).

        Idempotencia: si la collection seleccionada coincide con la
        activa, no se hace nada — evita refresh innecesario al re-emitir
        el signal sobre la fila ya seleccionada.
        """
        if self._active_detail is None:
            # Primera vez: construir el detail y agregarlo al stack.
            self._active_detail = CollectionDetailView(ctx=self._ctx, collection=collection)
            self._content_stack.addWidget(self._active_detail)
        elif self._active_detail.collection.collection_id != collection.collection_id:
            # Cambio real de colección: propagar a los 5 tabs sin reconstruir.
            self._active_detail.set_active_collection(collection)
        # else: misma colección activa → idempotente, no hacer nada.

        self._content_stack.setCurrentWidget(self._active_detail)

    def _open_csv_import_dialog(self: MainWindow) -> None:
        """Abre el diálogo de import. Cuando termina, refresca el sidebar
        para que la collection nueva sea seleccionable."""
        dialog = CsvImportDialog(ctx=self._ctx, parent=self)
        dialog.import_completed.connect(self._on_import_completed)
        dialog.exec()

    def _on_import_completed(self: MainWindow, _reports: dict[str, CsvImportReport]) -> None:
        """Slot del signal `import_completed` del CsvImportDialog.

        Refresca el sidebar (la colección nueva debe aparecer). Si era
        la primera colección de la DB, la selecciona automáticamente
        para que el empty state desaparezca.
        """
        was_empty = self._selector.is_empty()
        self._selector.refresh()
        if was_empty and not self._selector.is_empty():
            self._selector.select_first()

    # ------------------------------------------------------------------
    # ABMs administrativos (Prompt 4b)
    # ------------------------------------------------------------------

    def _open_cards_abm(self: MainWindow) -> None:
        coll = self._active_detail.collection if self._active_detail else None
        dialog = CardsAbmView(ctx=self._ctx, initial_collection=coll, parent=self)
        dialog.exec()
        # Diferimos el refresh al próximo tick del event loop: si lo
        # ejecutamos en línea, repueblan tablas grandes mientras Qt
        # todavía está cerrando el modal y se traba el event loop.
        QTimer.singleShot(0, self._refresh_active_detail)

    def _open_collections_abm(self: MainWindow) -> None:
        dialog = CollectionsAbmView(ctx=self._ctx, parent=self)
        # Refrescar el sidebar mientras el ABM sigue abierto (la red secundaria
        # de `_after_collections_abm_close` se mantiene por si el signal no
        # llega por algún motivo).
        dialog.collections_changed.connect(self._selector.refresh)
        dialog.exec()
        # Capturamos el id activo ahora (snapshot, no después del timer)
        # para que un cambio sincrónico al active_detail entre tanto no
        # nos confunda — y diferimos todo el bloque que toca UI.
        active_id = self._active_detail.collection.collection_id if self._active_detail else None
        QTimer.singleShot(0, lambda: self._after_collections_abm_close(active_id))

    def _after_collections_abm_close(self: MainWindow, active_id: int | None) -> None:
        """Bloque diferido tras cerrar el ABM de colecciones.

        Reagrupa: refresh del sidebar + decidir si el detail activo
        sigue válido. Lo invoca `QTimer.singleShot(0, ...)` para que
        Qt termine el teardown del modal antes de tocar widgets.
        """
        self._selector.refresh()
        # Si la colección activa fue borrada, el detail queda obsoleto.
        if active_id is not None and self._ctx.collections.get_by_id(active_id) is None:
            self._discard_active_detail()
        else:
            self._refresh_active_detail()

    def _open_codes_master_detail(self: MainWindow) -> None:
        dialog = CodesMasterDetailView(ctx=self._ctx, parent=self)
        dialog.exec()
        QTimer.singleShot(0, self._refresh_active_detail)

    def _refresh_active_detail(self: MainWindow) -> None:
        """Refresca los tabs del detail view activo, si hay uno.

        Patrón "alternativa simple" del plan: tras cerrar una ABM, los
        datos visibles en el detail pueden haber cambiado; refrescar
        todo es trivial para los volúmenes que manejamos.
        """
        if self._active_detail is None:
            return
        self._active_detail.refresh_all_tabs()

    def _discard_active_detail(self: MainWindow) -> None:
        """Quita el detail activo (la colección fue borrada)."""
        if self._active_detail is None:
            return
        self._content_stack.removeWidget(self._active_detail)
        self._active_detail.deleteLater()
        self._active_detail = None
        if self._selector.is_empty():
            return
        self._selector.select_first()

    # ------------------------------------------------------------------
    # API útil para tests / la siguiente sesión
    # ------------------------------------------------------------------

    @property
    def selector(self: MainWindow) -> CollectionSelectorView:
        return self._selector

    @property
    def active_detail(self: MainWindow) -> CollectionDetailView | None:
        return self._active_detail

    def is_showing_empty_state(self: MainWindow) -> bool:
        return self._content_stack.currentWidget() is self._empty_state
