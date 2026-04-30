"""Tab Estadísticas: progreso general, por código y top repetidas."""

import sqlite3

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CardsRepository,
    InventoryRepository,
)
from collections_app.core.services import InventoryService
from collections_app.shared_ui.theme import Spacing


class StatsView(QWidget):
    """Tab de estadísticas: progreso global, por código y top repetidas."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self.collection = collection
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def set_active_collection(self, collection: Collection) -> None:
        self.collection = collection
        self.refresh()

    def refresh(self) -> None:
        self._update_overall()
        self._update_per_code()
        self._update_top_duplicates()
        self._update_summary()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        body = QWidget()
        scroll.setWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.LG)

        layout.addWidget(self._make_section_label(self.tr("Progreso general")))
        self._overall_bar = QProgressBar()
        self._overall_bar.setMinimum(0)
        self._overall_bar.setMaximum(100)
        layout.addWidget(self._overall_bar)
        self._overall_label = QLabel("")
        layout.addWidget(self._overall_label)

        layout.addWidget(self._make_section_label(self.tr("Por código")))
        self._per_code_container = QWidget()
        self._per_code_layout = QVBoxLayout(self._per_code_container)
        self._per_code_layout.setContentsMargins(0, 0, 0, 0)
        self._per_code_layout.setSpacing(Spacing.XS)
        layout.addWidget(self._per_code_container)

        layout.addWidget(self._make_section_label(self.tr("Top repetidas")))
        self._top_dup_container = QWidget()
        self._top_dup_layout = QVBoxLayout(self._top_dup_container)
        self._top_dup_layout.setContentsMargins(0, 0, 0, 0)
        self._top_dup_layout.setSpacing(Spacing.XS)
        layout.addWidget(self._top_dup_container)

        layout.addWidget(self._make_section_label(self.tr("Resumen de inventario")))
        self._summary_label = QLabel("")
        layout.addWidget(self._summary_label)
        layout.addStretch()

    def _make_section_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setStyleSheet("font-weight: bold; font-size: 13pt;")
        return label

    # ------------------------------------------------------------------
    # Refresco
    # ------------------------------------------------------------------

    def _update_overall(self) -> None:
        assert self.collection.collection_id is not None
        stats = InventoryService(self.conn).get_stats(self.collection.collection_id)
        total = int(stats["total_cards"])
        owned = int(stats["owned"])
        pct = float(stats["percentage"])
        self._overall_bar.setMaximum(max(total, 1))
        self._overall_bar.setValue(owned)
        self._overall_label.setText(
            self.tr("{owned}/{total} ({pct:.1f}%)").format(owned=owned, total=total, pct=pct)
        )

    def _update_per_code(self) -> None:
        assert self.collection.collection_id is not None
        self._clear_layout(self._per_code_layout)
        stats = CardsRepository(self.conn).get_stats_by_code(self.collection.collection_id)
        for entry in stats:
            row = self._make_per_code_row(
                code_id=entry["code_id"],
                code_name=entry["code_name"],
                owned=entry["owned"],
                total=entry["total"],
                percentage=entry["percentage"],
            )
            self._per_code_layout.addWidget(row)

    def _make_per_code_row(
        self,
        code_id: str,
        code_name: str,
        owned: int,
        total: int,
        percentage: float,
    ) -> QWidget:
        container = QFrame()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(f"{code_id} — {code_name}")
        label.setMinimumWidth(180)
        layout.addWidget(label)

        bar = QProgressBar()
        bar.setMinimum(0)
        bar.setMaximum(max(total, 1))
        bar.setValue(owned)
        bar.setTextVisible(False)
        layout.addWidget(bar, stretch=1)

        layout.addWidget(
            QLabel(self.tr("{o}/{t} ({p:.0f}%)").format(o=owned, t=total, p=percentage))
        )
        return container

    def _update_top_duplicates(self) -> None:
        assert self.collection.collection_id is not None
        self._clear_layout(self._top_dup_layout)
        inv_repo = InventoryRepository(self.conn)
        items = inv_repo.get_top_duplicates(self.collection.collection_id, limit=10)
        if not items:
            self._top_dup_layout.addWidget(QLabel(self.tr("(sin repetidas todavía)")))
            return
        cards_repo = CardsRepository(self.conn)
        for item in items:
            card = cards_repo.get(self.collection.collection_id, item.code_id, item.card_number)
            name = card.card_name if card else ""
            self._top_dup_layout.addWidget(
                QLabel(
                    f"{item.code_id}-{item.card_number} {name} ".ljust(40, ".")
                    + f" x{item.quantity}"
                )
            )

    def _update_summary(self) -> None:
        assert self.collection.collection_id is not None
        stats = InventoryService(self.conn).get_stats(self.collection.collection_id)
        total_physical = int(stats["total_physical"])
        owned = int(stats["owned"])
        extras = int(stats["total_duplicate_copies"])
        self._summary_label.setText(
            self.tr(
                "Total figuritas físicas: {tp}\n"
                "Cards únicas (que tenés): {own}\n"
                "Copias extra (repetidas): {ex}"
            ).format(tp=total_physical, own=owned, ex=extras)
        )

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget() if child else None
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
