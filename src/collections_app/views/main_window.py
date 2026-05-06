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

Cuando el usuario cambia de colección desde el sidebar, **se destruye
y se recrea** el `CollectionDetailView` (decisión del plan: sin estado
fantasma entre colecciones; signals viejos quedan colgados sobre un
widget eliminado y Qt los limpia).

El título refleja el profile activo:
- profile None → "Collections"
- profile != None → "Collections — [<nombre>]"
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from collections_app.app_context import AppContext
from collections_app.core.models.collection import Collection
from collections_app.views.collections.collection_detail_view import (
    CollectionDetailView,
)
from collections_app.views.collections.collection_selector import (
    CollectionSelectorView,
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
        archivo = self.menuBar().addMenu(self.tr("&Archivo"))
        nueva = archivo.addAction(self.tr("&Nueva colección desde CSV..."))
        nueva.triggered.connect(self._show_csv_placeholder)
        archivo.addSeparator()
        salir = archivo.addAction(self.tr("&Salir"))
        salir.triggered.connect(self.close)

    def _wire_signals(self: MainWindow) -> None:
        self._selector.collection_selected.connect(self._on_collection_selected)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_collection_selected(self: MainWindow, collection: Collection) -> None:
        """Reemplaza el detail view activo. Destruye el previo si había uno."""
        if self._active_detail is not None:
            self._content_stack.removeWidget(self._active_detail)
            self._active_detail.deleteLater()
            self._active_detail = None

        detail = CollectionDetailView(ctx=self._ctx, collection=collection)
        self._active_detail = detail
        self._content_stack.addWidget(detail)
        self._content_stack.setCurrentWidget(detail)

    def _show_csv_placeholder(self: MainWindow) -> None:
        QMessageBox.information(
            self,
            self.tr("Importar CSV"),
            self.tr("La importación de colecciones desde CSV se implementa en Prompt 4."),
        )

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
