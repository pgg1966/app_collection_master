"""Diálogo de propuesta de intercambio (Prompt 5b).

Modal grande que se abre tras importar un `.colexchange` válido.
Muestra dos grillas LADO A LADO (HBox, no apiladas):

- "Necesito" — `cards_to_receive`: lo que el otro coleccionista
  tiene de más y vos necesitás.
- "Ofrezco"  — `cards_to_give`: lo que vos tenés de más y el otro
  coleccionista necesita.

Cada grilla usa `ExchangeProposalTableModel` con 3 columnas
(checkbox / identificador / nombre). Defaults: todas las filas
tildadas. El usuario puede destildar lo que no quiera intercambiar.

Al pie hay un resumen dinámico ("Recibís N · Entregás M") y un
botón "Ejecutar intercambio" que se deshabilita si la suma de
selecciones es 0.

Errores del apply (`InsufficientInventory` por mutación concurrente
del inventario, p. ej. desde el tab "Cargar stock") se muestran como
QMessageBox.critical y NO cierran el dialog — el usuario puede
destildar y reintentar.

Si tras `accept()` el dialog quedó con un evento aplicado, el caller
puede leer `applied_event_id`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.models.aggregates.exchange_proposal import (
    ExchangeProposal,
)
from collections_app.services.exchange_errors import InsufficientInventory
from collections_app.views.exchange.proposal_table_model import (
    ExchangeProposalTableModel,
)

if TYPE_CHECKING:
    from collections_app.app_context import AppContext
    from collections_app.core.models.collection import Collection


_WARNINGS_PREVIEW = 5  # Cantidad de warnings que se muestran inicialmente.


class ExchangeProposalDialog(QDialog):
    """Modal con la propuesta editable post-import."""

    def __init__(
        self: ExchangeProposalDialog,
        ctx: AppContext,
        collection: Collection,
        proposal: ExchangeProposal,
        warnings: tuple[str, ...] = (),
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ctx = ctx
        self._collection = collection
        self._proposal = proposal
        self._warnings = warnings
        self.applied_event_id: int | None = None
        self.setWindowTitle(self.tr("Propuesta de intercambio"))
        self.resize(900, 540)
        self._build_ui()
        self._update_summary_and_button()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self: ExchangeProposalDialog) -> None:
        outer = QVBoxLayout(self)

        if self._warnings:
            outer.addWidget(self._build_warnings_banner())

        # Dos grillas lado a lado.
        grids = QHBoxLayout()
        grids.addLayout(
            self._build_grid(
                title=self.tr("Necesito"),
                rows=self._proposal.cards_to_receive,
                attr_name="_receive_model",
                table_attr="_receive_table",
            )
        )
        grids.addLayout(
            self._build_grid(
                title=self.tr("Ofrezco"),
                rows=self._proposal.cards_to_give,
                attr_name="_give_model",
                table_attr="_give_table",
            )
        )
        outer.addLayout(grids, 1)

        self._summary_label = QLabel("")
        outer.addWidget(self._summary_label)

        btns = QHBoxLayout()
        btns.addStretch()
        self._cancel_btn = QPushButton(self.tr("Cancelar"))
        self._cancel_btn.clicked.connect(self.reject)
        self._apply_btn = QPushButton(self.tr("Ejecutar intercambio"))
        self._apply_btn.setDefault(True)
        self._apply_btn.clicked.connect(self._on_apply)
        btns.addWidget(self._cancel_btn)
        btns.addWidget(self._apply_btn)
        outer.addLayout(btns)

    def _build_grid(
        self: ExchangeProposalDialog,
        *,
        title: str,
        rows: tuple,  # type: ignore[type-arg]  # tuple[ProposedExchange, ...]
        attr_name: str,
        table_attr: str,
    ) -> QVBoxLayout:
        col = QVBoxLayout()
        title_label = QLabel(f"<b>{title}</b>")
        col.addWidget(title_label)

        model = ExchangeProposalTableModel(
            rows=rows,
            requires_code=bool(self._collection.requires_code),
        )
        setattr(self, attr_name, model)
        model.selection_changed.connect(self._update_summary_and_button)

        table = QTableView()
        table.setModel(model)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        # Pero la columna 0 (checkbox) sí responde por flags(); EditTriggers
        # no afecta toggle de checkbox.
        table.setAlternatingRowColors(True)
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        setattr(self, table_attr, table)
        col.addWidget(table)
        return col

    def _build_warnings_banner(self: ExchangeProposalDialog) -> QFrame:
        """Banner con las primeras N advertencias + botón "Ver todas" si hay más.

        Las advertencias extra viven en un `QFrame` separado oculto por
        default; el botón sólo togglea la visibilidad de ese contenedor.
        """
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(frame)
        header = QLabel(
            self.tr(
                "Hay {n} card(s) del archivo que no existen en tu colección "
                "y se ignoraron en el matching:"
            ).format(n=len(self._warnings))
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        preview = self._warnings[:_WARNINGS_PREVIEW]
        for w in preview:
            line = QLabel(f"• {w}")
            line.setWordWrap(True)
            layout.addWidget(line)

        if len(self._warnings) > _WARNINGS_PREVIEW:
            self._extra_container = QFrame()
            extra_layout = QVBoxLayout(self._extra_container)
            extra_layout.setContentsMargins(0, 0, 0, 0)
            for w in self._warnings[_WARNINGS_PREVIEW:]:
                line = QLabel(f"• {w}")
                line.setWordWrap(True)
                extra_layout.addWidget(line)
            self._extra_container.setVisible(False)
            layout.addWidget(self._extra_container)

            self._toggle_btn = QPushButton(self.tr("Ver todas ({n})").format(n=len(self._warnings)))
            self._toggle_btn.setCheckable(True)
            self._toggle_btn.toggled.connect(self._toggle_extra_warnings)
            layout.addWidget(self._toggle_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        return frame

    def _toggle_extra_warnings(self: ExchangeProposalDialog, show: bool) -> None:
        """Muestra/oculta el contenedor con advertencias más allá del preview."""
        self._extra_container.setVisible(show)
        self._toggle_btn.setText(
            self.tr("Ocultar") if show else self.tr("Ver todas ({n})").format(n=len(self._warnings))
        )

    # ------------------------------------------------------------------
    # Resumen + estado del botón
    # ------------------------------------------------------------------

    def _update_summary_and_button(self: ExchangeProposalDialog) -> None:
        n_recv = self._receive_model.total_selected_quantity()
        n_give = self._give_model.total_selected_quantity()
        self._summary_label.setText(
            self.tr("Recibís {r} card(s) · Entregás {g} card(s)").format(r=n_recv, g=n_give)
        )
        self._apply_btn.setEnabled((n_recv + n_give) > 0)

    # ------------------------------------------------------------------
    # Apply
    # ------------------------------------------------------------------

    def _on_apply(self: ExchangeProposalDialog) -> None:
        n_recv = self._receive_model.total_selected_quantity()
        n_give = self._give_model.total_selected_quantity()
        confirm = QMessageBox.question(
            self,
            self.tr("Confirmar intercambio"),
            self.tr(
                "¿Aplicar el intercambio?\n\nRecibís {r} card(s).\nEntregás {g} card(s)."
            ).format(r=n_recv, g=n_give),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        filtered = ExchangeProposal(
            cards_to_receive=tuple(self._receive_model.selected_rows()),
            cards_to_give=tuple(self._give_model.selected_rows()),
        )
        assert self._collection.collection_id is not None
        try:
            result = self._ctx.exchange_apply.apply_proposal(
                proposal=filtered,
                collection_id=self._collection.collection_id,
            )
        except InsufficientInventory as exc:
            QMessageBox.critical(
                self,
                self.tr("No se pudo aplicar el intercambio"),
                self.tr(
                    "El inventario cambió desde que abriste la propuesta.\n\n"
                    "Detalle: {msg}\n\n"
                    "Cerrá la propuesta y volvé a importar el archivo."
                ).format(msg=exc),
            )
            return
        self.applied_event_id = result.exchange_event_id
        self.accept()
