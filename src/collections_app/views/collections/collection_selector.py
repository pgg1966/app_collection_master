"""Sidebar de selección de colección.

`QListWidget` con los nombres de todas las colecciones disponibles.
Emite `collection_selected(Collection)` cuando el usuario hace click
o presiona Enter en una fila.

La MainWindow conecta ese signal y reemplaza el `CollectionDetailView`
del área de contenido. La selección NO se persiste entre runs en MVP
(queda en backlog si los usuarios lo piden).

Recibe `CollectionsService` directamente (no el `AppContext` entero)
porque es lo único que consume — patrón "ask only what you need" a
nivel inyección.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models.collection import Collection
from collections_app.services.collections_service import CollectionsService

_COLLECTION_DATA_ROLE = Qt.ItemDataRole.UserRole + 1


class CollectionSelectorView(QWidget):
    """Sidebar con la lista de colecciones disponibles."""

    # Emitido cuando el usuario activa una fila (click o Enter).
    collection_selected = Signal(Collection)

    def __init__(
        self: CollectionSelectorView,
        collections_service: CollectionsService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = collections_service
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self: CollectionSelectorView) -> None:
        outer = QVBoxLayout(self)
        outer.addWidget(QLabel(self.tr("Colecciones")))

        self._list = QListWidget()
        self._list.itemActivated.connect(self._emit_for_item)
        self._list.itemDoubleClicked.connect(self._emit_for_item)
        outer.addWidget(self._list, stretch=1)

        toolbar = QHBoxLayout()
        self._open_btn = QPushButton(self.tr("Abrir"))
        self._open_btn.clicked.connect(self._emit_for_current)
        self._refresh_btn = QPushButton(self.tr("Refrescar"))
        self._refresh_btn.clicked.connect(self.refresh)
        toolbar.addWidget(self._open_btn)
        toolbar.addWidget(self._refresh_btn)
        toolbar.addStretch()
        outer.addLayout(toolbar)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def refresh(self: CollectionSelectorView) -> None:
        """Vuelve a leer la lista desde el service y repuebla el QListWidget."""
        self._list.clear()
        for coll in self._service.list_all():
            item = QListWidgetItem(coll.collection_name)
            item.setData(_COLLECTION_DATA_ROLE, coll)
            self._list.addItem(item)

    def is_empty(self: CollectionSelectorView) -> bool:
        return self._list.count() == 0

    def select_first(self: CollectionSelectorView) -> Collection | None:
        """Selecciona la primera fila programáticamente y la emite. Útil al
        arrancar la MainWindow cuando hay >=1 colección. Retorna la
        Collection seleccionada, o None si no había ninguna."""
        if self._list.count() == 0:
            return None
        self._list.setCurrentRow(0)
        item = self._list.item(0)
        coll = self._collection_for_item(item)
        if coll is not None:
            self.collection_selected.emit(coll)
        return coll

    # ------------------------------------------------------------------
    # Slots internos
    # ------------------------------------------------------------------

    def _emit_for_item(self: CollectionSelectorView, item: QListWidgetItem) -> None:
        coll = self._collection_for_item(item)
        if coll is not None:
            self.collection_selected.emit(coll)

    def _emit_for_current(self: CollectionSelectorView) -> None:
        item = self._list.currentItem()
        if item is None:
            return
        self._emit_for_item(item)

    @staticmethod
    def _collection_for_item(item: QListWidgetItem) -> Collection | None:
        data = item.data(_COLLECTION_DATA_ROLE)
        return data if isinstance(data, Collection) else None
