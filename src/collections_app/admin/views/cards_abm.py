"""ABM concreto de Cards: combo de colección + ABM + import CSV."""

import logging
import sqlite3
from pathlib import Path

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.admin.tools.csv_importer import CardsCsvImporter, CsvImportResult
from collections_app.core.models import Card, Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    CollectionsRepository,
)
from collections_app.shared_ui import AbmConfig, AbmWidget, FieldDef, FieldType
from collections_app.shared_ui.theme import Spacing

logger = logging.getLogger(__name__)


class CardsAbmView(QWidget):
    """Vista para administrar cards de una colección.

    Layout:
        Combo de colección + botón Importar CSV
        AbmWidget reconstruido cuando cambia la colección (porque los
        choices del combo `code_id` dependen del header de la colección).
    """

    def __init__(self, conn: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.conn = conn
        self._current_collection: Collection | None = None
        self._cards_widget: AbmWidget | None = None
        # Retiene referencias a widgets descartados al cambiar de colección
        # para que sigan siendo padres válidos de cualquier evento pendiente
        # (Qt + Python GC + signals async = crashes en Windows si liberamos
        # demasiado pronto).
        self._discarded_widgets: list[AbmWidget] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addLayout(self._build_top_bar())

        self._abm_container = QVBoxLayout()
        self._abm_container.setContentsMargins(0, 0, 0, 0)
        root.addLayout(self._abm_container, stretch=1)

        self.refresh_collections_combo()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802 — Qt naming
        """Refresca el combo cada vez que el tab se hace visible."""
        super().showEvent(event)
        self.refresh_collections_combo()

    # ------------------------------------------------------------------
    # Top bar
    # ------------------------------------------------------------------

    def _build_top_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)

        layout.addWidget(QLabel(self.tr("Colección") + ":"))
        self._collection_combo = QComboBox()
        self._collection_combo.setMinimumWidth(280)
        self._collection_combo.currentIndexChanged.connect(self._on_collection_changed)
        layout.addWidget(self._collection_combo)

        layout.addStretch()

        self._import_button = QPushButton(self.tr("Importar CSV…"))
        self._import_button.clicked.connect(self._import_csv)
        self._import_button.setEnabled(False)
        layout.addWidget(self._import_button)
        return layout

    def refresh_collections_combo(self) -> None:
        """Re-popula el combo de colecciones desde la DB.

        Preserva la selección actual si la `collection_id` sigue existiendo
        (refresca el cache del nombre por si fue editada). Si la colección
        activa fue borrada, vuelve a "(ninguna)" y el AbmWidget se
        deshabilita.
        """
        previous_id = self._current_collection.collection_id if self._current_collection else None

        repo = CollectionsRepository(self.conn)
        all_collections = repo.list_all()
        all_ids = {c.collection_id for c in all_collections if c.collection_id is not None}

        self._collection_combo.blockSignals(True)
        self._collection_combo.clear()
        self._collection_combo.addItem(self.tr("(seleccione una colección)"), userData=None)
        for col in all_collections:
            self._collection_combo.addItem(col.collection_name, userData=col.collection_id)

        if previous_id is not None and previous_id in all_ids:
            # La colección sigue existiendo: preservar selección y refrescar
            # el cache local (puede haber cambiado de nombre).
            idx = self._collection_combo.findData(previous_id)
            self._collection_combo.setCurrentIndex(idx)
            self._collection_combo.blockSignals(False)
            self._current_collection = repo.get_by_id(previous_id)
            return

        # Sin selección previa, o la selección previa fue borrada.
        self._collection_combo.setCurrentIndex(0)
        self._collection_combo.blockSignals(False)
        self._current_collection = None
        self._import_button.setEnabled(False)
        self._clear_abm()

    # ------------------------------------------------------------------
    # Selección de colección → reconstrucción del AbmWidget
    # ------------------------------------------------------------------

    def _on_collection_changed(self, idx: int) -> None:
        collection_id = self._collection_combo.itemData(idx)
        if collection_id is None:
            self._current_collection = None
            self._import_button.setEnabled(False)
            self._clear_abm()
            return

        collection = CollectionsRepository(self.conn).get_by_id(int(collection_id))
        if collection is None:
            return

        self._current_collection = collection
        self._import_button.setEnabled(True)
        self._rebuild_cards_abm()

    def _clear_abm(self) -> None:
        if self._cards_widget is not None:
            self._cards_widget.blockSignals(True)
            self._abm_container.removeWidget(self._cards_widget)
            self._cards_widget.hide()
            # Lo retenemos en una lista para no liberar el QObject mientras
            # hay events pendientes; se libera cuando el view padre muere.
            self._discarded_widgets.append(self._cards_widget)
            self._cards_widget = None

    def _rebuild_cards_abm(self) -> None:
        assert self._current_collection is not None
        assert self._current_collection.collection_id is not None
        cid: int = self._current_collection.collection_id
        header_id = self._current_collection.code_header_id

        lines = CodesLinesRepository(self.conn).list_by_header(header_id)
        code_choices: list[tuple[str, object]] = [
            (f"{line.code_id} — {line.code_name}", line.code_id) for line in lines
        ]

        config = AbmConfig(
            title=self.tr("ABM Cards de {name}").format(
                name=self._current_collection.collection_name
            ),
            module_code="CARD001",
            fields=[
                FieldDef(
                    "code_id",
                    "Código",
                    FieldType.COMBO,
                    is_id=True,
                    combo_choices=code_choices,
                    grid_width=130,
                ),
                FieldDef(
                    "card_number",
                    "Número",
                    FieldType.INT,
                    is_id=True,
                    grid_width=80,
                ),
                FieldDef(
                    "card_name",
                    "Nombre",
                    FieldType.TEXT,
                    max_length=200,
                    grid_width=300,
                ),
            ],
            filter_field="card_name",
            filter_label=self.tr("Buscar por nombre"),
            on_load_all=lambda: CardsRepository(self.conn).list_by_collection(cid),
            on_save=self._save_card,
            on_delete=self._delete_card,
            model_class=Card,
            extra_kwargs={"collection_id": cid},
        )

        self._clear_abm()
        self._cards_widget = AbmWidget(config, parent=self)
        self._abm_container.addWidget(self._cards_widget)

    def _save_card(self, card: Card) -> Card:
        saved = CardsRepository(self.conn).upsert(card)
        self.conn.commit()
        return saved

    def _delete_card(self, card: Card) -> bool:
        ok = CardsRepository(self.conn).delete(card.collection_id, card.code_id, card.card_number)
        self.conn.commit()
        return ok

    # ------------------------------------------------------------------
    # Import CSV
    # ------------------------------------------------------------------

    def _import_csv(self) -> None:
        if self._current_collection is None:
            return

        path_str, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Importar cards desde CSV"),
            "",
            self.tr("CSV files (*.csv)"),
        )
        if not path_str:
            return

        progress = QProgressDialog(
            self.tr("Importando cards…"),
            self.tr("Cancelar"),
            0,
            100,
            self,
        )
        progress.setWindowModality(progress.windowModality())
        progress.setMinimumDuration(0)

        def _update(current: int, total: int) -> None:
            if total > 0:
                progress.setMaximum(total)
                progress.setValue(current)

        assert self._current_collection.collection_id is not None
        cid: int = self._current_collection.collection_id
        importer = CardsCsvImporter(self.conn)
        try:
            result = importer.import_file(
                Path(path_str),
                cid,
                on_progress=_update,
            )
        except Exception as exc:  # noqa: BLE001
            progress.close()
            QMessageBox.critical(self, self.tr("Error"), str(exc))
            logger.exception("Error importando CSV")
            return

        progress.close()
        self._show_import_result(result)
        if self._cards_widget is not None:
            self._cards_widget.refresh()

    def _show_import_result(self, result: CsvImportResult) -> None:
        text = self.tr(
            "Importación completada.\n" "Total: {total}\nImportadas: {ok}\nOmitidas: {skipped}"
        ).format(
            total=result.total_rows,
            ok=result.imported,
            skipped=result.skipped,
        )
        if result.errors:
            sample = "\n".join(result.errors[:10])
            text += "\n\n" + self.tr("Primeros errores:") + "\n" + sample
        QMessageBox.information(self, self.tr("Importar CSV"), text)
