"""Tests del OcrLoaderTab — smoke de los 3 estados.

Cero subprocess real, cero modelo cargado: los stubs del state-detection
deciden qué página mostrar y validamos que la UI corresponde.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.views.inventory.ocr_loader_tab import (
    _PAGE_INSTALL,
    _PAGE_NO_MODEL,
    _PAGE_READY,
    OcrLoaderTab,
    _format_install_error,
)

pytestmark = pytest.mark.gui


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx_and_collection() -> Iterator[tuple[AppContext, Collection]]:
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


def test_state_install_when_dependencies_missing(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Sin torch/ultralytics → página de instalación."""
    monkeypatch.setattr(
        "collections_app.views.inventory.ocr_loader_tab.OcrInstallService.is_installed",
        staticmethod(lambda: False),
    )
    ctx, coll = ctx_and_collection
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert tab._stack.currentIndex() == _PAGE_INSTALL
    assert tab._install_btn.isHidden() is False


def test_state_no_model_when_deps_ok_but_no_model(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Deps OK + collection sin OCR configurado → página informativa."""
    monkeypatch.setattr(
        "collections_app.views.inventory.ocr_loader_tab.OcrInstallService.is_installed",
        staticmethod(lambda: True),
    )
    ctx, coll = ctx_and_collection
    # ctx no tiene `get_ocr_service` todavía (commit 9 lo agrega) →
    # _get_ocr_service devuelve None → cae a Estado 2.
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert tab._stack.currentIndex() == _PAGE_NO_MODEL
    assert "no tiene un modelo" in tab._no_model_label.text()


def test_state_ready_when_deps_ok_and_model_present(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Deps OK + factory devuelve un OcrService real → página de carga."""
    monkeypatch.setattr(
        "collections_app.views.inventory.ocr_loader_tab.OcrInstallService.is_installed",
        staticmethod(lambda: True),
    )
    ctx, coll = ctx_and_collection
    # Stub de la factory: devolvemos un objeto cualquiera (no se invoca).
    monkeypatch.setattr(
        ctx.__class__,
        "get_ocr_service",
        lambda self, _coll: object(),
        raising=False,
    )
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert tab._stack.currentIndex() == _PAGE_READY
    assert tab._add_photos_btn.isHidden() is False


def test_set_active_collection_re_evaluates_state(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Cambiar de collection refresca el estado."""
    state = {"installed": False}
    monkeypatch.setattr(
        "collections_app.views.inventory.ocr_loader_tab.OcrInstallService.is_installed",
        staticmethod(lambda: state["installed"]),
    )
    ctx, coll = ctx_and_collection
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert tab._stack.currentIndex() == _PAGE_INSTALL

    # Cambiamos el flag, set_active_collection debe re-evaluar.
    state["installed"] = True
    tab.set_active_collection(coll)
    assert tab._stack.currentIndex() == _PAGE_NO_MODEL


def test_card_changed_signal_exists(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """El wrapper LoaderTab necesita re-emitir este signal."""
    monkeypatch.setattr(
        "collections_app.views.inventory.ocr_loader_tab.OcrInstallService.is_installed",
        staticmethod(lambda: False),
    )
    ctx, coll = ctx_and_collection
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert hasattr(tab, "card_changed")


# ---------------------------------------------------------------------
# _InferenceWorker — fix cross-thread sqlite (post-smoke 5d)
# ---------------------------------------------------------------------


def test_inference_worker_passes_db_path_to_run_inference(
    ctx_and_collection: tuple[AppContext, Collection],
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    """El worker pasa `db_path` (no Connection) a `OcrService.run_inference`.

    `run_inference` abre su propia conn internamente — el worker solo
    tiene que pasarle el path del ctx. Esto evita el cross-thread
    error de SQLite.
    """
    from collections_app.views.inventory.ocr_loader_tab import _InferenceWorker

    ctx, coll = ctx_and_collection
    assert coll.collection_id is not None

    received: dict[str, object] = {}

    class _FakeOcr:
        def run_inference(self, _img, *, db_path, collection_id):  # type: ignore[no-untyped-def]
            received["db_path"] = db_path
            received["cid"] = collection_id
            return ([], [])

    image = tmp_path / "x.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    worker = _InferenceWorker(
        ocr_service=_FakeOcr(),  # type: ignore[arg-type]
        image_path=image,
        db_path=ctx.db_path,
        collection_id=coll.collection_id,
    )

    finished_payloads: list[tuple[list, list]] = []
    worker.finished.connect(lambda d, e: finished_payloads.append((d, e)))

    worker.run()

    assert received["db_path"] == ctx.db_path
    assert received["cid"] == coll.collection_id
    assert finished_payloads == [([], [])]


def test_inference_worker_emits_failed_on_ocr_error(
    ctx_and_collection: tuple[AppContext, Collection],
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    """Si `run_inference` lanza OcrError, el worker emite `failed`."""
    from collections_app.services.exceptions import OcrModelError
    from collections_app.views.inventory.ocr_loader_tab import _InferenceWorker

    ctx, coll = ctx_and_collection
    assert coll.collection_id is not None

    class _FakeOcr:
        def run_inference(self, *_a, **_k):  # type: ignore[no-untyped-def]
            raise OcrModelError("modelo roto")

    image = tmp_path / "x.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    worker = _InferenceWorker(
        ocr_service=_FakeOcr(),  # type: ignore[arg-type]
        image_path=image,
        db_path=ctx.db_path,
        collection_id=coll.collection_id,
    )
    failures: list[str] = []
    worker.failed.connect(lambda msg: failures.append(msg))

    worker.run()

    assert failures == ["modelo roto"]


# ---------------------------------------------------------------------
# _format_install_error — traducción del WinError 5
# ---------------------------------------------------------------------


def test_format_install_error_passes_through_normal_message() -> None:
    """Sin pistas de acceso denegado, el mensaje se devuelve tal cual."""
    msg = "el comando falló (código 1):\nERROR: package not found"
    assert _format_install_error(msg) == msg


def test_format_install_error_translates_winerror_5() -> None:
    """Si el error trae WinError 5, agregar pasos para resolverlo manualmente."""
    raw = "el comando falló (código 1):\nWinError 5: cv2.pyd is locked"
    out = _format_install_error(raw)
    assert "Acceso denegado" in out
    assert "Cerrar la app" in out
    assert "PowerShell como administrador" in out
    assert ".venv\\Scripts\\pip install easyocr opencv-python" in out
    # El mensaje original queda incluido como detalle técnico.
    assert "WinError 5" in out


def test_format_install_error_translates_acceso_denegado_es() -> None:
    """También dispara con la traducción en español."""
    raw = "el comando falló:\nAcceso denegado: cv2.pyd"
    out = _format_install_error(raw)
    assert "Cerrar la app" in out
    assert "Acceso denegado" in out


# ---------------------------------------------------------------------
# _populate_results_table — defaults post-smoke 5d
# ---------------------------------------------------------------------


def _make_detection(
    *,
    code_id: str = "KOR",
    card_number: int = 6,
    confidence: float = 0.5,
    card_id: int | None = 42,
    card_name: str = "Park",
    bbox: tuple[int, int, int, int] = (0, 0, 10, 10),
):  # type: ignore[no-untyped-def]
    from collections_app.core.models.ocr_detection import OcrDetection

    return OcrDetection(
        raw_label=f"{code_id} {card_number}",
        code_id=code_id,
        card_number=card_number,
        confidence=confidence,
        card_name=card_name,
        card_id=card_id,
        bbox=bbox,
    )


def test_populate_marks_all_rows_checked_by_default(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Todas las filas vienen Checked por default, sin importar confidence."""
    from PySide6.QtCore import Qt

    monkeypatch.setattr(
        "collections_app.views.inventory.ocr_loader_tab.OcrInstallService.is_installed",
        staticmethod(lambda: True),
    )
    monkeypatch.setattr(
        ctx_and_collection[0].__class__,
        "get_ocr_service",
        lambda self, _coll: object(),
        raising=False,
    )
    ctx, coll = ctx_and_collection
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)

    detections = [
        _make_detection(confidence=0.92),  # alta
        _make_detection(confidence=0.50),  # baja (antes hubiera quedado destildada)
        _make_detection(confidence=0.27, card_id=None, card_name=""),  # no en catálogo
    ]
    tab._populate_results_table(detections)

    for row in range(tab._results_table.rowCount()):
        item = tab._results_table.item(row, 0)
        assert item is not None
        assert item.checkState() == Qt.CheckState.Checked


def test_populate_unknown_card_rows_styled_in_orange(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Filas con card_id=None se renderizan en naranja + itálica."""
    from collections_app.views.inventory.ocr_loader_tab import _UNKNOWN_CARD_COLOR

    monkeypatch.setattr(
        "collections_app.views.inventory.ocr_loader_tab.OcrInstallService.is_installed",
        staticmethod(lambda: True),
    )
    monkeypatch.setattr(
        ctx_and_collection[0].__class__,
        "get_ocr_service",
        lambda self, _coll: object(),
        raising=False,
    )
    ctx, coll = ctx_and_collection
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)

    detections = [
        _make_detection(card_id=99, card_name="Real"),  # en catálogo
        _make_detection(card_id=None, card_name=""),  # NO en catálogo
    ]
    tab._populate_results_table(detections)

    # Fila 0 (en catálogo): texto sin tinte naranja, no itálica.
    code_known = tab._results_table.item(0, 1)
    assert code_known is not None
    assert code_known.foreground().color().name().upper() != _UNKNOWN_CARD_COLOR.upper()
    assert code_known.font().italic() is False

    # Fila 1 (NO en catálogo): naranja + itálica en las 3 columnas de texto.
    for col in (1, 2, 3):
        item = tab._results_table.item(1, col)
        assert item is not None
        assert item.foreground().color().name().upper() == _UNKNOWN_CARD_COLOR.upper()
        assert item.font().italic() is True
