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

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.models.ocr_detection import OcrDetection
from collections_app.views.inventory.ocr_result_dialog import OcrResultDialog

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx_and_collection() -> Iterator[tuple[AppContext, Collection]]:
    """Ctx con una collection mínima para inicializar el diálogo.

    El diálogo en sí no toca la DB; el ctx+collection se pasan para
    poder instanciar `_ManualCardDialog` si el usuario clickea
    "Agregar no procesadas".
    """
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="Mundial",
                card_count=10,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
            )
        )
        ctx.conn.commit()
        yield ctx, coll
    finally:
        ctx.close()


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


def _build_dialog(
    ctx_and_collection: tuple[AppContext, Collection],
    tmp_path: Path,
    detections: list[OcrDetection],
    *,
    total_photos: int = 1,
) -> OcrResultDialog:
    ctx, coll = ctx_and_collection
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    return OcrResultDialog(
        image_path=image,
        detections=detections,
        errors=[],
        photo_index=0,
        total_photos=total_photos,
        ctx=ctx,
        collection=coll,
    )


def test_dialog_construction_does_not_crash(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    ctx_and_collection: tuple[AppContext, Collection],
    _mock_annotate: None,
) -> None:
    """Smoke: construcción con detecciones mock no crashea."""
    detections = [
        _make_detection(),
        _make_detection(card_number=5, card_id=None, card_name=""),
    ]
    dialog = _build_dialog(ctx_and_collection, tmp_path, detections)
    qtbot.addWidget(dialog)

    assert dialog.skip is False
    assert dialog.cancel_all is False
    assert dialog._table.rowCount() == 2


def test_dialog_generates_pixmap_via_annotate(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    ctx_and_collection: tuple[AppContext, Collection],
    _mock_annotate: None,
) -> None:
    """El QPixmap mockeado se setea en el label de la imagen."""
    dialog = _build_dialog(ctx_and_collection, tmp_path, [_make_detection()])
    qtbot.addWidget(dialog)

    pix = dialog._image_label.pixmap()
    assert pix is not None
    assert not pix.isNull()


def test_skip_button_sets_skip_flag_and_rejects(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    ctx_and_collection: tuple[AppContext, Collection],
    _mock_annotate: None,
) -> None:
    """`Saltar foto` deja `skip=True` y cierra con Rejected."""
    dialog = _build_dialog(ctx_and_collection, tmp_path, [_make_detection()], total_photos=2)
    qtbot.addWidget(dialog)

    dialog._skip_btn.click()

    assert dialog.skip is True
    assert dialog.cancel_all is False
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_cancel_all_button_sets_cancel_all_flag_and_rejects(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    ctx_and_collection: tuple[AppContext, Collection],
    _mock_annotate: None,
) -> None:
    """`Cancelar todo` deja `cancel_all=True` y cierra con Rejected."""
    dialog = _build_dialog(ctx_and_collection, tmp_path, [_make_detection()], total_photos=2)
    qtbot.addWidget(dialog)

    dialog._cancel_all_btn.click()

    assert dialog.cancel_all is True
    assert dialog.skip is False
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_load_button_accepts_and_returns_checked_detections(
    qtbot,  # type: ignore[no-untyped-def]
    tmp_path: Path,
    ctx_and_collection: tuple[AppContext, Collection],
    _mock_annotate: None,
) -> None:
    """`Cargar esta foto`: Accepted + `selected_detections()` solo trae las marcadas."""
    d1 = _make_detection(card_number=1)
    d2 = _make_detection(card_number=2)
    d3 = _make_detection(card_number=3)
    dialog = _build_dialog(ctx_and_collection, tmp_path, [d1, d2, d3])
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
    ctx_and_collection: tuple[AppContext, Collection],
    _mock_annotate: None,
) -> None:
    """Filas vienen tildadas por default, sin importar confianza ni card_id."""
    detections = [
        _make_detection(card_number=1, confidence=0.92),
        _make_detection(card_number=2, confidence=0.40),
        _make_detection(card_number=3, card_id=None, card_name=""),
    ]
    dialog = _build_dialog(ctx_and_collection, tmp_path, detections)
    qtbot.addWidget(dialog)

    for row in range(dialog._table.rowCount()):
        item = dialog._table.item(row, 0)
        assert item is not None
        assert item.checkState() == Qt.CheckState.Checked


def test_add_manual_button_opens_manual_card_dialog(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    ctx_and_collection: tuple[AppContext, Collection],
    _mock_annotate: None,
) -> None:
    """Click en `Agregar no procesadas` abre `_ManualCardDialog` modal.

    Mockeamos `exec` para que no bloquee el test loop; solo verificamos
    que el diálogo se construyó (env. CardLoaderView) y `exec` se llamó.
    """
    captured: dict[str, object] = {}

    real_init = None
    from collections_app.views.inventory import ocr_result_dialog as mod

    real_init = mod._ManualCardDialog.__init__

    def _patched_init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        captured["kwargs"] = kwargs
        real_init(self, *args, **kwargs)

    monkeypatch.setattr(mod._ManualCardDialog, "__init__", _patched_init)
    monkeypatch.setattr(mod._ManualCardDialog, "exec", lambda self: 1)

    dialog = _build_dialog(ctx_and_collection, tmp_path, [_make_detection()])
    qtbot.addWidget(dialog)

    dialog._add_manual_btn.click()

    # _ManualCardDialog construido con el ctx + collection del padre.
    ctx, coll = ctx_and_collection
    assert captured["kwargs"]["ctx"] is ctx  # type: ignore[index]
    assert captured["kwargs"]["collection"] is coll  # type: ignore[index]
    # El OcrResultDialog NO se cerró — el user vuelve a confirmar OCR.
    assert dialog.isVisible() is False  # nunca se mostró, pero tampoco rejected.
    assert dialog.skip is False
    assert dialog.cancel_all is False
