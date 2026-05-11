"""Diálogo de verificación post-procesamiento de una foto (Prompt 6 / B).

Modal que se abre después de que YOLO + EasyOCR procesan una foto.
Muestra a la izquierda la foto con bounding boxes anotados (verde
si confidence ≥ 0.70, naranja si menor); a la derecha la tabla de
detecciones con checkboxes para que el usuario revise antes de
aplicar.

Tres salidas:

- `dialog.exec() == Accepted` + `selected_detections()` → aplicar
  las filas tildadas.
- `dialog.exec() == Rejected` con `dialog.skip = True` → saltar
  esta foto y procesar la siguiente.
- `dialog.exec() == Rejected` con `dialog.cancel_all = True` →
  cancelar el procesamiento de todas las fotos pendientes.

`_annotate_image` importa cv2 LAZY (regla del Prompt 5d / arch
test). En tests se mockea para evitar cargar cv2 real.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPixmap, QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from collections_app.app_context import AppContext
    from collections_app.core.models.collection import Collection
    from collections_app.core.models.ocr_detection import OcrDetection, OcrParseError


_CONFIDENCE_HIGH = 0.70
# Colores BGR (cv2 usa BGR, no RGB). Verde → high confidence, naranja → low.
_BBOX_COLOR_HIGH = (0, 200, 0)
_BBOX_COLOR_LOW = (0, 165, 255)
# Color naranja en UI para filas con card_id=None (consistente con la
# tabla anterior del OcrLoaderTab).
_UNKNOWN_CARD_COLOR = "#D97706"

_HEADERS = ["", "Código", "Nombre", "Confianza"]
_COL_CHECK = 0
_COL_CODE = 1
_COL_NAME = 2
_COL_CONF = 3


class _ScaledImageLabel(QLabel):
    """QLabel que re-escala su pixmap al tamaño disponible.

    El QLabel default no re-escala el pixmap cuando el widget cambia de
    tamaño; setScaledContents=True ignora el aspect ratio. Esta subclase
    guarda el pixmap original y re-escala en cada resizeEvent preservando
    proporción.
    """

    def __init__(self: _ScaledImageLabel, pixmap: QPixmap, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._original = pixmap
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        # Mínimo chico — el splitter define el tamaño real.
        self.setMinimumSize(1, 1)
        # Mostrar el pixmap antes del primer resize (si esperamos al
        # resizeEvent, el label queda vacío hasta que el dialog se
        # muestra; en tests no se llega a mostrar nunca).
        if not pixmap.isNull():
            super().setPixmap(pixmap)

    def resizeEvent(self: _ScaledImageLabel, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        if not self._original.isNull():
            scaled = self._original.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            super().setPixmap(scaled)


class _ManualCardDialog(QDialog):
    """Envuelve `CardLoaderView` en un modal para usarlo desde el flow OCR.

    El usuario abre este popup desde el botón "Agregar no procesadas" del
    `OcrResultDialog` cuando una card no fue detectada por YOLO/OCR y
    quiere agregarla manualmente sin abortar el batch. `CardLoaderView`
    aplica las altas directamente al inventario (vista preservada de
    v0.1, CLAUDE.md §7.1 — no se modifica). Al cerrar, el usuario vuelve
    al `OcrResultDialog` para confirmar las detecciones OCR.
    """

    def __init__(
        self: _ManualCardDialog,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        # Import lazy para evitar el ciclo
        # views/inventory/ocr_result_dialog.py ⇄ views/inventory/card_loader.py
        # — ambos terminan importados por OcrLoaderTab.
        from collections_app.views.inventory.card_loader import (  # noqa: PLC0415
            CardLoaderView,
        )

        self.setWindowTitle(self.tr("Agregar carta manualmente"))
        self.setModal(True)
        self.resize(650, 420)

        layout = QVBoxLayout(self)
        self._loader = CardLoaderView(ctx=ctx, collection=collection)
        layout.addWidget(self._loader)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton(self.tr("Cerrar"))
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)


class OcrResultDialog(QDialog):
    """Modal: foto anotada + tabla de detecciones + 4 botones."""

    def __init__(
        self: OcrResultDialog,
        image_path: Path,
        detections: list[OcrDetection],
        errors: list[OcrParseError],
        photo_index: int,
        total_photos: int,
        ctx: AppContext,
        collection: Collection,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._image_path = image_path
        self._detections = list(detections)
        self._errors = list(errors)
        self._photo_index = photo_index
        self._total_photos = total_photos
        # ctx + collection se usan para instanciar `_ManualCardDialog`
        # cuando el usuario clickea "Agregar no procesadas".
        self._ctx = ctx
        self._collection = collection
        # Flags de salida (Rejected). Sin estos, `exec()` solo informa
        # Accepted/Rejected y el caller no sabría si fue skip o cancel.
        self.skip = False
        self.cancel_all = False

        self.setWindowTitle(self.tr("Verificar detecciones"))
        self._resize_to_screen()
        self._build_ui()

    def _resize_to_screen(self: OcrResultDialog) -> None:
        """Tamaño inicial = 85% ancho × 80% alto de la pantalla principal."""
        screen = QApplication.primaryScreen()
        if screen is None:  # defensive — entornos sin display
            self.resize(1200, 800)
            return
        geo = screen.availableGeometry()
        self.resize(int(geo.width() * 0.85), int(geo.height() * 0.80))

    def _build_ui(self: OcrResultDialog) -> None:
        outer = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Izquierda: foto anotada en un widget que re-escala con el
        # panel. Si la imagen no se pudo leer, fallback a un QLabel
        # con texto explicativo.
        annotated = self._annotate_image()
        if annotated is not None and not annotated.isNull():
            self._image_label: QLabel = _ScaledImageLabel(annotated)
        else:
            self._image_label = QLabel(self.tr("(no se pudo cargar la imagen)"))
            self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        splitter.addWidget(self._image_label)

        # Derecha: header + tabla. Los botones del flow viven en el
        # QVBoxLayout principal (fuera del splitter) para que siempre
        # sean visibles, sin importar qué tamaño tomen las dos
        # secciones del splitter.
        right = QWidget()
        right_layout = QVBoxLayout(right)
        n_with_card = sum(1 for d in self._detections if d.card_id is not None)
        n_total = len(self._detections)
        header_text = self.tr("Detectadas: {n}").format(n=n_total)
        if n_with_card != n_total:
            header_text += self.tr("  ({k} en catálogo local)").format(k=n_with_card)
        if self._errors:
            header_text += self.tr("  · {e} no reconocidas").format(e=len(self._errors))
        right_layout.addWidget(QLabel(header_text))

        self._table = QTableWidget(len(self._detections), len(_HEADERS))
        self._table.setHorizontalHeaderLabels(_HEADERS)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(_COL_CHECK, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_CODE, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(_COL_NAME, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(_COL_CONF, QHeaderView.ResizeMode.ResizeToContents)
        self._populate_table()
        right_layout.addWidget(self._table, 1)

        splitter.addWidget(right)
        # Proporciones iniciales: foto ~55%, tabla ~45%. Qt escala
        # estos valores proporcionalmente al ancho real del splitter.
        splitter.setSizes([55, 45])
        outer.addWidget(splitter, 1)

        outer.addWidget(
            QLabel(
                self.tr("Foto {n} de {total}: {name}").format(
                    n=self._photo_index + 1,
                    total=self._total_photos,
                    name=self._image_path.name,
                )
            )
        )

        # Botones del flow — fuera del splitter, fixed height.
        btn_row = QHBoxLayout()
        self._cancel_all_btn = QPushButton(self.tr("Cancelar todo"))
        self._cancel_all_btn.clicked.connect(self._on_cancel_all)
        self._skip_btn = QPushButton(self.tr("Saltar foto"))
        self._skip_btn.clicked.connect(self._on_skip)
        self._add_manual_btn = QPushButton(self.tr("Agregar no procesadas"))
        self._add_manual_btn.clicked.connect(self._on_add_manual)
        self._load_btn = QPushButton(self.tr("Cargar esta foto"))
        self._load_btn.setDefault(True)
        self._load_btn.clicked.connect(self.accept)
        btn_row.addWidget(self._cancel_all_btn)
        btn_row.addWidget(self._skip_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._add_manual_btn)
        btn_row.addWidget(self._load_btn)
        outer.addLayout(btn_row)

    def _populate_table(self: OcrResultDialog) -> None:
        """Llena la tabla con las detecciones — checkboxes en Checked.

        Filas con `card_id=None` se renderizan en naranja + itálica
        (mismo patrón que la tabla inline anterior).
        """
        unknown_brush = QBrush(QColor(_UNKNOWN_CARD_COLOR))
        italic = QFont()
        italic.setItalic(True)
        for row, d in enumerate(self._detections):
            check = QTableWidgetItem("")
            check.setFlags(check.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            check.setCheckState(Qt.CheckState.Checked)
            self._table.setItem(row, _COL_CHECK, check)

            code_text = f"{d.code_id}-{d.card_number}" if d.code_id else str(d.card_number)
            code_item = QTableWidgetItem(code_text)
            name_item = QTableWidgetItem(d.card_name or self.tr("(no encontrada)"))
            conf_item = QTableWidgetItem(f"{int(d.confidence * 100)}%")

            if d.card_id is None:
                for item in (code_item, name_item, conf_item):
                    item.setForeground(unknown_brush)
                    item.setFont(italic)

            self._table.setItem(row, _COL_CODE, code_item)
            self._table.setItem(row, _COL_NAME, name_item)
            self._table.setItem(row, _COL_CONF, conf_item)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_skip(self: OcrResultDialog) -> None:
        self.skip = True
        self.reject()

    def _on_cancel_all(self: OcrResultDialog) -> None:
        self.cancel_all = True
        self.reject()

    def _on_add_manual(self: OcrResultDialog) -> None:
        """Abre el popup de alta manual sin cerrar este diálogo.

        El popup envuelve `CardLoaderView` y aplica las altas
        directamente al inventario. Al cerrarse, el usuario vuelve a
        este diálogo para terminar de revisar las detecciones OCR.
        """
        dlg = _ManualCardDialog(ctx=self._ctx, collection=self._collection, parent=self)
        dlg.exec()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def selected_detections(self: OcrResultDialog) -> list[OcrDetection]:
        """Detecciones cuyo checkbox quedó marcado al cerrar."""
        out: list[OcrDetection] = []
        for row, d in enumerate(self._detections):
            check = self._table.item(row, _COL_CHECK)
            if check is not None and check.checkState() == Qt.CheckState.Checked:
                out.append(d)
        return out

    # ------------------------------------------------------------------
    # Foto anotada
    # ------------------------------------------------------------------

    def _annotate_image(self: OcrResultDialog) -> QPixmap | None:
        """Lee la foto, dibuja rectángulos sobre las detecciones y
        devuelve un `QPixmap`.

        Devuelve `None` si la imagen no se puede leer (foto corrupta,
        path inválido, etc.). El UI maneja ese caso mostrando un
        placeholder de texto.
        """
        import cv2  # noqa: PLC0415

        img = cv2.imread(str(self._image_path))
        if img is None:
            return None

        for d in self._detections:
            x1, y1, x2, y2 = d.bbox
            color = _BBOX_COLOR_HIGH if d.confidence >= _CONFIDENCE_HIGH else _BBOX_COLOR_LOW
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                img,
                d.raw_label,
                (x1, max(0, y1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
            )

        # cv2 entrega BGR; Qt espera RGB.
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, _ch = img_rgb.shape
        # Import lazy de QImage para no traer Qt al testear esta función
        # con imágenes mockeadas. (En la práctica QImage ya está
        # disponible vía PySide6.QtGui — el lazy es solo conceptual.)
        from PySide6.QtGui import QImage  # noqa: PLC0415

        # bytesPerLine = ancho * channels (3 para RGB888).
        qimg = QImage(
            img_rgb.tobytes(),
            w,
            h,
            3 * w,
            QImage.Format.Format_RGB888,
        )
        return QPixmap.fromImage(qimg)
