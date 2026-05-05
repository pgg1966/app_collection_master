"""Dialog modal de bienvenida para perfiles nuevos sin colecciones.

Se muestra una sola vez al arrancar el cliente con un perfil cuya DB
no tiene colecciones (típico tras `--profile <nuevo>`). Permite:

  1. Importar la estructura (colecciones, codes, cards) desde otro
     perfil existente — el inventario NO se importa, el usuario empieza
     con stock cero.
  2. Empezar vacío — la app sigue su flujo normal (que va a abrir el
     dialog de elegir colección, que estará vacío hasta que el admin
     cargue catálogo).

El botón X de la ventana está oculto para forzar una decisión explícita.
Tras cerrar (con cualquiera de las dos opciones), `main.py` setea el
flag `setup_completed=1` en app_settings así no vuelve a aparecer.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from collections_app.core.db.connection import create_connection
from collections_app.core.services.profile_service import (
    ProfileInfo,
    ProfileService,
)
from collections_app.shared_ui.theme import Spacing, StatusColor

logger = logging.getLogger(__name__)


class _ImportWorker(QThread):
    """Importa la estructura en un thread separado para no bloquear la UI.

    Abre su propia conexión al target_db (NO recibe `sqlite3.Connection`
    del hilo principal — convención del proyecto). El target ya tiene
    el schema aplicado (las migraciones corrieron al inicializar la
    conexión principal).
    """

    finished_ok = Signal(int)  # cantidad de colecciones importadas
    failed = Signal(str)

    def __init__(
        self,
        source_db_path: Path,
        target_db_path: Path,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._source = source_db_path
        self._target = target_db_path

    def run(self) -> None:
        try:
            conn = create_connection(self._target)
            try:
                count = ProfileService.import_structure(self._source, conn)
            finally:
                conn.close()
            self.finished_ok.emit(count)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error importando estructura desde %s", self._source)
            self.failed.emit(str(exc))


class ProfileSetupDialog(QDialog):
    """Dialog de primera corrida para perfiles sin colecciones.

    Pasamos `target_db_path` (no la conexión) porque el worker abre su
    propia conexión en el thread del importador. Filtramos los perfiles
    disponibles: excluye el perfil actual y los que no tienen colecciones
    (no tendría sentido importar de un perfil vacío).
    """

    def __init__(
        self,
        current_profile: str,
        available_profiles: list[ProfileInfo],
        target_db_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(self.tr("Configurar perfil"))
        self.setMinimumWidth(440)
        self.setModal(True)
        # Sin botón X para forzar decisión explícita (Importar/Empezar vacío).
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        self._target_db_path = target_db_path
        self._available = [
            p for p in available_profiles if p.name != current_profile and p.collection_count > 0
        ]
        self._radio_group: QButtonGroup | None = None
        self._worker: _ImportWorker | None = None
        self._build_ui(current_profile)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self, current_profile: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        title = QLabel(self.tr('Bienvenido al perfil "{p}"').format(p=current_profile))
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel(
            self.tr(
                "Este perfil no tiene colecciones configuradas.\n"
                "Podés importar la estructura desde otro perfil "
                "(sin inventario — empezás desde cero)."
            )
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        if self._available:
            layout.addWidget(QLabel(self.tr("Importar desde:")))
            self._radio_group = QButtonGroup(self)
            for i, profile in enumerate(self._available):
                inv_text = (
                    self.tr("tiene datos") if profile.has_inventory else self.tr("sin inventario")
                )
                radio = QRadioButton(
                    f"{profile.display_name}  "
                    f"({profile.collection_count} {self.tr('colecciones')}, "
                    f"{inv_text})"
                )
                if i == 0:
                    radio.setChecked(True)
                self._radio_group.addButton(radio, i)
                layout.addWidget(radio)
        else:
            no_profiles = QLabel(
                self.tr(
                    "No hay otros perfiles con colecciones disponibles.\n"
                    "Podés configurar las colecciones desde la app Admin."
                )
            )
            no_profiles.setWordWrap(True)
            no_profiles.setStyleSheet("color: gray;")
            layout.addWidget(no_profiles)

        # Barra de progreso indeterminada (oculta hasta importar).
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.hide()
        layout.addWidget(self._progress)

        self._status_label = QLabel("")
        self._status_label.setWordWrap(True)
        layout.addWidget(self._status_label)

        # Botones inferiores
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_import = QPushButton(self.tr("Importar estructura"))
        self._btn_import.setEnabled(bool(self._available))
        self._btn_import.clicked.connect(self._on_import)
        btn_row.addWidget(self._btn_import)

        self._btn_empty = QPushButton(self.tr("Empezar vacío"))
        self._btn_empty.clicked.connect(self.accept)
        btn_row.addWidget(self._btn_empty)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def _on_import(self) -> None:
        if self._radio_group is None:
            return
        selected_id = self._radio_group.checkedId()
        if selected_id < 0 or selected_id >= len(self._available):
            return
        profile = self._available[selected_id]

        self._btn_import.setEnabled(False)
        self._btn_empty.setEnabled(False)
        self._progress.show()
        self._status_label.setText(self.tr("Importando…"))
        self._status_label.setStyleSheet("")

        self._worker = _ImportWorker(
            source_db_path=profile.db_path,
            target_db_path=self._target_db_path,
            parent=self,
        )
        self._worker.finished_ok.connect(self._on_import_done)
        self._worker.failed.connect(self._on_import_failed)
        self._worker.start()

    def _on_import_done(self, count: int) -> None:
        self._progress.hide()
        self._status_label.setText(
            self.tr("✓ {n} colecciones importadas correctamente.").format(n=count)
        )
        self._status_label.setStyleSheet(f"color: {StatusColor.SUCCESS};")
        # Pequeña pausa para que el usuario vea el mensaje de éxito.
        QTimer.singleShot(1200, self, self.accept)

    def _on_import_failed(self, error: str) -> None:
        self._progress.hide()
        self._btn_import.setEnabled(True)
        self._btn_empty.setEnabled(True)
        self._status_label.setText(self.tr("Error al importar: {e}").format(e=error))
        self._status_label.setStyleSheet(f"color: {StatusColor.ERROR};")
