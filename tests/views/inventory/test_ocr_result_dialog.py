"""Tests del `OcrResultDialog` — popup post-procesamiento (Prompt 6 / B3).

Smoke de la API pública del diálogo: flags de salida (`skip`,
`cancel_all`) y `selected_detections()`. `_annotate_image` se mockea
para no levantar cv2 en tests.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QDialog

from collections_app.core.models.ocr_detection import OcrDetection
from collections_app.views.inventory.ocr_result_dialog import OcrResultDialog

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


def _make_detection(
    *,
    code_id: str = "ARG",
    card_number: int = 4,
    confidence: float = 0.9,
    card_id: int | None = 42,
    card_name: str = "Messi",
    bbox: tuple[int, int, int, int] = (10, 10, 100, 60),
) -> OcrDetection:
    return OcrDetection(
        raw_label=f"{code_id}-{card_number}",
        code_id=code_id,
        card_number=card_number,
        confidence=confidence,
        card_name=card_name,
        card_id=card_id,
        bbox=bbox,
    )


@pytest.fixture
def _mock_annotate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reemplaza `_annotate_image` por un QPixmap vacío.

    Sin esto, el diálogo intenta `import cv2` y `cv2.imread`, lo que en
    CI no aporta — solo nos interesa la interacción con los botones y
    la tabla. El test específico de pixmap (más abajo) sí ejercita el
    happy path con un QPixmap real.
    """
    monkeypatch.setattr(
        OcrResultDialog,
        "_annotate_image",
        lambda self: QPixmap(10, 10),
    )


def test_dialog_construction_does_not_crash(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    _mock_annotate: None,
) -> None:
    """Smoke: construcción con detecciones mock no crashea."""
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    detections = [_make_detection(), _make_detection(card_number=5, card_id=None, card_name="")]

    dialog = OcrResultDialog(
        image_path=image,
        detections=detections,
        errors=[],
        photo_index=0,
        total_photos=1,
    )
    qtbot.addWidget(dialog)

    assert dialog.skip is False
    assert dialog.cancel_all is False
    assert dialog._table.rowCount() == 2


def test_dialog_generates_pixmap_via_annotate(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    _mock_annotate: None,
) -> None:
    """El QPixmap mockeado se setea en el label de la imagen."""
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")

    dialog = OcrResultDialog(
        image_path=image,
        detections=[_make_detection()],
        errors=[],
        photo_index=0,
        total_photos=1,
    )
    qtbot.addWidget(dialog)

    pix = dialog._image_label.pixmap()
    assert pix is not None
    assert not pix.isNull()


def test_skip_button_sets_skip_flag_and_rejects(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    _mock_annotate: None,
) -> None:
    """`Saltar foto` deja `skip=True` y cierra con Rejected."""
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")

    dialog = OcrResultDialog(
        image_path=image,
        detections=[_make_detection()],
        errors=[],
        photo_index=0,
        total_photos=2,
    )
    qtbot.addWidget(dialog)

    dialog._skip_btn.click()

    assert dialog.skip is True
    assert dialog.cancel_all is False
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_cancel_all_button_sets_cancel_all_flag_and_rejects(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    _mock_annotate: None,
) -> None:
    """`Cancelar todo` deja `cancel_all=True` y cierra con Rejected."""
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")

    dialog = OcrResultDialog(
        image_path=image,
        detections=[_make_detection()],
        errors=[],
        photo_index=0,
        total_photos=2,
    )
    qtbot.addWidget(dialog)

    dialog._cancel_all_btn.click()

    assert dialog.cancel_all is True
    assert dialog.skip is False
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_load_button_accepts_and_returns_checked_detections(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    _mock_annotate: None,
) -> None:
    """`Cargar esta foto`: Accepted + `selected_detections()` solo trae las marcadas."""
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")

    d1 = _make_detection(card_number=1)
    d2 = _make_detection(card_number=2)
    d3 = _make_detection(card_number=3)

    dialog = OcrResultDialog(
        image_path=image,
        detections=[d1, d2, d3],
        errors=[],
        photo_index=0,
        total_photos=1,
    )
    qtbot.addWidget(dialog)

    # Destildamos la fila del medio.
    item = dialog._table.item(1, 0)
    assert item is not None
    item.setCheckState(Qt.CheckState.Unchecked)

    dialog._load_btn.click()

    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.skip is False
    assert dialog.cancel_all is False
    selected = dialog.selected_detections()
    assert selected == [d1, d3]


def test_all_rows_checked_by_default(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    _mock_annotate: None,
) -> None:
    """Filas vienen tildadas por default, sin importar confianza ni card_id."""
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")

    detections = [
        _make_detection(card_number=1, confidence=0.92),
        _make_detection(card_number=2, confidence=0.40),
        _make_detection(card_number=3, card_id=None, card_name=""),
    ]
    dialog = OcrResultDialog(
        image_path=image,
        detections=detections,
        errors=[],
        photo_index=0,
        total_photos=1,
    )
    qtbot.addWidget(dialog)

    for row in range(dialog._table.rowCount()):
        item = dialog._table.item(row, 0)
        assert item is not None
        assert item.checkState() == Qt.CheckState.Checked
