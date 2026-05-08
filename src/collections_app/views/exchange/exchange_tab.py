"""Tab "Intercambio" en `CollectionDetailView` (Prompt 5b).

Dos botones grandes lado a lado:

- "Generar archivo": abre `ExchangeExportDialog` y, si tiene éxito,
  encadena `ExchangeSuccessDialog` con el path resultante.
- "Importar archivo": file picker → valida con
  `ExchangeImportService` → arma snapshot local con
  `InventorySnapshotService` → calcula propuesta con `MatchingService`
  → abre `ExchangeProposalDialog`.

La tab no tiene estado propio que mostrar (por eso no implementa
`refresh()`), pero sí emite `inventory_changed` después de un apply
exitoso para que `CollectionDetailView` refresque las tabs lectoras
(Mis cards, Historial, Estadísticas, Reportes).

Errores del import se traducen a mensajes orientados al usuario
(invalid file, unsupported version, collection not found, OSError).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.services.exchange_errors import (
    CollectionNotFound,
    InvalidExchangeFile,
    UnsupportedFormatVersion,
)
from collections_app.services.matching_service import MatchingService
from collections_app.views.exchange.export_dialog import ExchangeExportDialog
from collections_app.views.exchange.proposal_dialog import ExchangeProposalDialog
from collections_app.views.exchange.success_dialog import ExchangeSuccessDialog

if TYPE_CHECKING:
    from collections_app.app_context import AppContext
    from collections_app.core.models.collection import Collection


class ExchangeTab(QWidget):
    """Tab del detail que aloja los flows de generación e importación."""

    inventory_changed = Signal()

    def __init__(
        self: ExchangeTab,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._collection = collection
        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self: ExchangeTab) -> None:
        outer = QVBoxLayout(self)

        info = QLabel(
            self.tr(
                "Compartí tu inventario con otro coleccionista para calcular "
                "automáticamente qué pueden intercambiar.\n\n"
                "• Generá un archivo y mandáselo al otro coleccionista.\n"
                "• O importá el archivo que te haya mandado para ver "
                "la propuesta de intercambio."
            )
        )
        info.setWordWrap(True)
        outer.addWidget(info)

        outer.addStretch()

        btns = QHBoxLayout()
        self._export_btn = QPushButton(self.tr("Generar archivo"))
        self._export_btn.clicked.connect(self._on_export)
        self._import_btn = QPushButton(self.tr("Importar archivo"))
        self._import_btn.clicked.connect(self._on_import)
        btns.addStretch()
        btns.addWidget(self._export_btn)
        btns.addWidget(self._import_btn)
        btns.addStretch()
        outer.addLayout(btns)

        outer.addStretch()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_export(self: ExchangeTab) -> None:
        assert self._collection.collection_id is not None
        export_dlg = ExchangeExportDialog(
            ctx=self._ctx,
            collection_id=self._collection.collection_id,
            parent=self,
        )
        if export_dlg.exec() != export_dlg.DialogCode.Accepted:
            return
        path = export_dlg.result_path
        if path is None:
            return
        success_dlg = ExchangeSuccessDialog(
            path=path,
            collection_name=self._collection.collection_name,
            parent=self,
        )
        success_dlg.exec()

    def _on_import(self: ExchangeTab) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Importar archivo de intercambio"),
            "",
            self.tr("Archivos de intercambio (*.colexchange);;Todos los archivos (*)"),
        )
        if not path_str:
            return
        path = Path(path_str)

        try:
            import_result = self._ctx.exchange_import.read_from_file(path)
        except InvalidExchangeFile as exc:
            QMessageBox.critical(
                self,
                self.tr("Archivo inválido"),
                str(exc),
            )
            return
        except UnsupportedFormatVersion as exc:
            QMessageBox.information(
                self,
                self.tr("Versión no soportada"),
                str(exc),
            )
            return
        except CollectionNotFound as exc:
            QMessageBox.warning(
                self,
                self.tr("Colección no instalada"),
                str(exc),
            )
            return
        except OSError as exc:
            QMessageBox.critical(
                self,
                self.tr("Error de I/O"),
                self.tr("No se pudo leer el archivo: {msg}").format(msg=exc),
            )
            return

        # La colección viene del archivo; el caller hizo lookup local. Si la
        # tab está abierta sobre OTRA collection, igual respetamos la del
        # archivo para que el matching sea coherente con su catálogo.
        if import_result.local_collection_id != self._collection.collection_id:
            QMessageBox.warning(
                self,
                self.tr("Colección no coincide"),
                self.tr(
                    "El archivo es de la colección «{name}», pero estás "
                    "viendo otra colección. Cambiá a la correcta para "
                    "importar."
                ).format(name=import_result.snapshot.collection_name),
            )
            return

        # Snapshot LOCAL para alimentar el matching.
        assert self._collection.collection_id is not None
        my_snapshot = self._ctx.inventory_snapshot.build_local_snapshot(
            collection_id=self._collection.collection_id,
            user_label=None,
        )
        proposal = MatchingService.calculate_proposal(
            my_inventory=my_snapshot,
            their_inventory=import_result.snapshot,
        )

        if not proposal.cards_to_receive and not proposal.cards_to_give:
            QMessageBox.information(
                self,
                self.tr("Sin coincidencias"),
                self.tr(
                    "El matching no encontró cards para intercambiar entre "
                    "tu inventario y el del archivo."
                ),
            )
            return

        proposal_dlg = ExchangeProposalDialog(
            ctx=self._ctx,
            collection=self._collection,
            proposal=proposal,
            warnings=import_result.warnings,
            parent=self,
        )
        if proposal_dlg.exec() == proposal_dlg.DialogCode.Accepted:
            self.inventory_changed.emit()

    # ------------------------------------------------------------------
    # API pública (consistencia con los otros tabs)
    # ------------------------------------------------------------------

    def set_active_collection(self: ExchangeTab, collection: Collection) -> None:
        """Cambia la colección activa. La tab no tiene estado a recargar."""
        self._collection = collection
