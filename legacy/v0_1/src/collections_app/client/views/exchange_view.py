"""ExchangeView: dialog modal para ejecutar un intercambio entre dos usuarios.

Pre-puebla las dos grillas (Entrego / Recibo) con el `ComparisonResult`
del CompareView. Al abrir bloquea las cartas a entregar en inventario;
al cerrar (cancelar/X) las desbloquea automáticamente. Solo "Ejecutar
intercambio" hace cambios persistentes en inventario.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.db.connection import create_connection
from collections_app.core.models import (
    Collection,
    ComparisonResult,
    ExchangeCard,
    ExchangeSession,
)
from collections_app.core.repositories import (
    CardsRepository,
)
from collections_app.core.services import ExchangeService
from collections_app.shared_ui.theme import Spacing, StatusColor

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Worker para ejecutar el intercambio (no bloquea UI)
# ----------------------------------------------------------------------


class _ExecuteExchangeWorker(QThread):
    """Ejecuta `ExchangeService.execute_exchange` en thread separado."""

    finished_ok = Signal()
    failed = Signal(str)

    def __init__(
        self,
        db_path: Path,
        collection_id: int,
        session: ExchangeSession,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._db_path = db_path
        self._collection_id = collection_id
        self._session = session

    def run(self) -> None:
        try:
            conn = create_connection(self._db_path)
            try:
                ExchangeService(conn).execute_exchange(self._collection_id, self._session)
            finally:
                conn.close()
            self.finished_ok.emit()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error ejecutando intercambio")
            self.failed.emit(str(exc))


# ----------------------------------------------------------------------
# Dialog auxiliar: agregar carta manual al intercambio
# ----------------------------------------------------------------------


class _AddCardDialog(QDialog):
    """Mini-form para buscar una carta en el catálogo y agregarla al intercambio.

    No reusa el CardLoaderView completo (sería overkill — ese maneja
    inventario, transactions, ambigüedad, completer, etc.). Acá solo
    necesitamos: pedir un (code_id, card_number) válido contra el
    catálogo y devolver la `ExchangeCard` correspondiente.
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        title: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._conn = conn
        self._collection = collection
        self._result: ExchangeCard | None = None

        self.setWindowTitle(title)
        self._build_ui()

    @property
    def result_card(self) -> ExchangeCard | None:
        return self._result

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        form = QHBoxLayout()
        if self._collection.requires_code:
            form.addWidget(QLabel(self.tr("Código") + ":"))
            self._code_edit = QLineEdit()
            self._code_edit.setMaxLength(10)
            self._code_edit.setFixedWidth(80)
            form.addWidget(self._code_edit)
        else:
            self._code_edit = None  # type: ignore[assignment]
        form.addWidget(QLabel(self.tr("Número") + ":"))
        self._number_edit = QLineEdit()
        self._number_edit.setFixedWidth(80)
        form.addWidget(self._number_edit)
        form.addStretch()
        layout.addLayout(form)

        self._info_label = QLabel("")
        self._info_label.setWordWrap(True)
        layout.addWidget(self._info_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self) -> None:
        number_text = self._number_edit.text().strip()
        try:
            number = int(number_text)
        except ValueError:
            self._info_label.setText(self.tr("Número inválido"))
            self._info_label.setStyleSheet(f"color: {StatusColor.WARNING};")
            return

        cards_repo = CardsRepository(self._conn)
        assert self._collection.collection_id is not None
        cid = self._collection.collection_id

        if self._collection.requires_code:
            code_id = (self._code_edit.text() or "").strip().upper()
            if not code_id:
                self._info_label.setText(self.tr("Código vacío"))
                self._info_label.setStyleSheet(f"color: {StatusColor.WARNING};")
                return
            card = cards_repo.get(cid, code_id, number)
            if card is None:
                self._info_label.setText(
                    self.tr("{c}-{n} no existe en el catálogo").format(c=code_id, n=number)
                )
                self._info_label.setStyleSheet(f"color: {StatusColor.ERROR};")
                return
        else:
            matches = cards_repo.find_by_number(cid, number)
            if not matches:
                self._info_label.setText(
                    self.tr("Número {n} no existe en el catálogo").format(n=number)
                )
                self._info_label.setStyleSheet(f"color: {StatusColor.ERROR};")
                return
            if len(matches) > 1:
                self._info_label.setText(
                    self.tr(
                        "Hay {n} cards con ese número, no se puede agregar sin "
                        "especificar código (caso ambiguo no soportado en intercambio)"
                    ).format(n=len(matches))
                )
                self._info_label.setStyleSheet(f"color: {StatusColor.WARNING};")
                return
            card = matches[0]

        self._result = ExchangeCard(
            code_id=card.code_id,
            card_number=card.card_number,
            card_name=card.card_name,
            quantity=1,
        )
        self.accept()


# ----------------------------------------------------------------------
# ExchangeView principal
# ----------------------------------------------------------------------


class ExchangeView(QDialog):
    """Dialog modal de ejecución de intercambio."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        db_path: Path,
        collection: Collection,
        comparison: ComparisonResult,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.conn = conn
        self._db_path = db_path
        self.collection = collection
        self._comparison = comparison
        self._exec_worker: _ExecuteExchangeWorker | None = None
        # Flag para distinguir cierres "esperados" (Ejecutar/Cancelar) de
        # cierres por la X — en el segundo caso necesitamos unlock.
        self._cleanup_done = False

        self.setWindowTitle(self.tr("Ejecutar Intercambio"))
        self.setMinimumSize(700, 500)
        self._build_ui()
        # Pre-poblar grillas + bloquear cartas a entregar.
        self._populate_initial()
        self._lock_initial_to_give()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        outer.setSpacing(Spacing.MD)

        # Dos columnas
        cols = QHBoxLayout()
        # Entrego
        give_layout = QVBoxLayout()
        give_layout.addWidget(QLabel("<b>" + self.tr("Entrego") + "</b>"))
        self._give_list = QListWidget()
        give_layout.addWidget(self._give_list, stretch=1)
        self._add_give_button = QPushButton(self.tr("+ Agregar figurita"))
        self._add_give_button.clicked.connect(self._on_add_give)
        give_layout.addWidget(self._add_give_button)

        # Recibo
        recv_layout = QVBoxLayout()
        recv_layout.addWidget(QLabel("<b>" + self.tr("Recibo") + "</b>"))
        self._recv_list = QListWidget()
        recv_layout.addWidget(self._recv_list, stretch=1)
        self._add_recv_button = QPushButton(self.tr("+ Agregar figurita"))
        self._add_recv_button.clicked.connect(self._on_add_recv)
        recv_layout.addWidget(self._add_recv_button)

        cols.addLayout(give_layout, stretch=1)
        cols.addLayout(recv_layout, stretch=1)
        outer.addLayout(cols, stretch=1)

        # Botones inferiores
        buttons = QHBoxLayout()
        self._exec_button = QPushButton(self.tr("✓ Ejecutar intercambio"))
        self._exec_button.clicked.connect(self._on_execute)
        cancel_button = QPushButton(self.tr("✕ Cancelar"))
        cancel_button.clicked.connect(self._on_cancel)
        buttons.addWidget(self._exec_button)
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        outer.addLayout(buttons)

    # ------------------------------------------------------------------
    # Estado inicial
    # ------------------------------------------------------------------

    def _populate_initial(self) -> None:
        """Pre-puebla las grillas con el ComparisonResult, todo chequeado."""
        for card in self._comparison.i_can_offer:
            self._add_card_to_list(self._give_list, card)
        for card in self._comparison.i_need:
            self._add_card_to_list(self._recv_list, card)

    def _lock_initial_to_give(self) -> None:
        """Bloquea en inventario las cartas pre-pobladas en `Entrego`."""
        if not self._comparison.i_can_offer:
            return
        assert self.collection.collection_id is not None
        ExchangeService(self.conn).lock_cards(
            self.collection.collection_id, self._comparison.i_can_offer
        )

    def _add_card_to_list(self, target: QListWidget, card: ExchangeCard) -> None:
        item = QListWidgetItem(self._format_card(card))
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked)
        # Guardamos el ExchangeCard en el data role para reconstruirlo.
        item.setData(Qt.ItemDataRole.UserRole, card)
        target.addItem(item)

    def _format_card(self, card: ExchangeCard) -> str:
        if self.collection.requires_code:
            label = f"{card.code_id}-{card.card_number}"
        else:
            label = str(card.card_number)
        return f"{label:<10} {card.card_name}"

    # ------------------------------------------------------------------
    # Agregar cartas manualmente
    # ------------------------------------------------------------------

    def _on_add_give(self) -> None:
        # Confirmación: el usuario está agregando una carta para regalar.
        confirm = QMessageBox.question(
            self,
            self.tr("Agregar figurita a entregar"),
            self.tr(
                "¿Seguro que querés agregar una carta para entregar?\n"
                "Se dará de baja del inventario al confirmar el intercambio."
            ),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        dlg = _AddCardDialog(
            self.conn,
            self.collection,
            self.tr("Agregar carta a entregar"),
            parent=self,
        )
        if not dlg.exec() or dlg.result_card is None:
            return
        card = dlg.result_card

        # Bloquear en inventario inmediatamente
        assert self.collection.collection_id is not None
        ExchangeService(self.conn).lock_cards(self.collection.collection_id, [card])
        self._add_card_to_list(self._give_list, card)

    def _on_add_recv(self) -> None:
        dlg = _AddCardDialog(
            self.conn,
            self.collection,
            self.tr("Agregar carta a recibir"),
            parent=self,
        )
        if not dlg.exec() or dlg.result_card is None:
            return
        self._add_card_to_list(self._recv_list, dlg.result_card)

    # ------------------------------------------------------------------
    # Ejecutar / Cancelar
    # ------------------------------------------------------------------

    def _checked_cards(self, target: QListWidget) -> list[ExchangeCard]:
        out: list[ExchangeCard] = []
        for i in range(target.count()):
            item = target.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                card = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(card, ExchangeCard):
                    out.append(card)
        return out

    def _on_execute(self) -> None:
        to_give = self._checked_cards(self._give_list)
        to_receive = self._checked_cards(self._recv_list)

        confirm = QMessageBox.question(
            self,
            self.tr("Confirmar intercambio"),
            self.tr(
                "¿Confirmás el intercambio?\n\n"
                "Entregás: {g} figurita(s)\n"
                "Recibís: {r} figurita(s)\n\n"
                "Esta acción no se puede deshacer."
            ).format(g=len(to_give), r=len(to_receive)),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        session = ExchangeSession(to_give=to_give, to_receive=to_receive)
        self._exec_button.setEnabled(False)

        assert self.collection.collection_id is not None
        worker = _ExecuteExchangeWorker(
            db_path=self._db_path,
            collection_id=self.collection.collection_id,
            session=session,
            parent=self,
        )
        self._exec_worker = worker

        def on_ok() -> None:
            QMessageBox.information(
                self,
                self.tr("Intercambio ejecutado"),
                self.tr("Intercambio ejecutado correctamente."),
            )
            self._cleanup_done = True
            self.accept()

        def on_failed(msg: str) -> None:
            self._exec_button.setEnabled(True)
            QMessageBox.critical(
                self,
                self.tr("Error al ejecutar"),
                self.tr("No se pudo ejecutar el intercambio:\n{m}").format(m=msg),
            )

        worker.finished_ok.connect(on_ok)
        worker.failed.connect(on_failed)
        worker.start()

    def _on_cancel(self) -> None:
        self._unlock_inventory()
        self._cleanup_done = True
        self.reject()

    def _unlock_inventory(self) -> None:
        """Resetea locked=0 para toda la colección."""
        assert self.collection.collection_id is not None
        try:
            ExchangeService(self.conn).unlock_all_cards(self.collection.collection_id)
        except Exception:
            logger.exception("Error desbloqueando inventario al cerrar dialog")

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 — Qt naming
        """Si se cierra con la X sin Ejecutar/Cancelar, desbloquear igual."""
        if not self._cleanup_done:
            self._unlock_inventory()
            self._cleanup_done = True
        super().closeEvent(event)
