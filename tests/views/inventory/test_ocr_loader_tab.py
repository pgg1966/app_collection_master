"""Tests del OcrLoaderTab — smoke de los 2 estados.

Cero modelo cargado: los stubs del state-detection deciden qué página
mostrar y validamos que la UI corresponde.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.views.inventory.ocr_loader_tab import (
    _PAGE_NO_MODEL,
    _PAGE_READY,
    OcrLoaderTab,
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


def test_state_no_model_when_factory_returns_none(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Factory `get_ocr_service` retorna None (sin modelo configurado) → Estado No-Model."""
    ctx, coll = ctx_and_collection
    # ctx real con la collection default (sin ocr_model_filename) → la factory
    # retorna None → cae al Estado No-Model variante A.
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert tab._stack.currentIndex() == _PAGE_NO_MODEL
    assert "no tiene un modelo" in tab._no_model_label.text()


def test_state_ready_when_factory_returns_service(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Factory devuelve un OcrService real → página de carga."""
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


def test_guide_image_hidden_when_no_guide_configured(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Sin `get_ocr_guide_path` o devolviendo None → el widget de guía está oculto."""
    ctx, coll = ctx_and_collection
    monkeypatch.setattr(
        ctx.__class__,
        "get_ocr_service",
        lambda self, _coll: object(),
        raising=False,
    )
    monkeypatch.setattr(
        ctx.__class__,
        "get_ocr_guide_path",
        lambda self, _coll: None,
        raising=False,
    )
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert tab._guide_image.isHidden() is True


def test_guide_image_shown_when_path_exists(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    """Con un path válido + imagen legible → el widget de guía se muestra."""
    from PySide6.QtGui import QImage

    ctx, coll = ctx_and_collection
    monkeypatch.setattr(
        ctx.__class__,
        "get_ocr_service",
        lambda self, _coll: object(),
        raising=False,
    )

    # Generar una imagen PNG válida via Qt (en vez de bytes mágicos).
    guide_path = tmp_path / "guide.png"
    qimg = QImage(100, 60, QImage.Format.Format_RGB888)
    qimg.fill(0)
    assert qimg.save(str(guide_path)) is True

    monkeypatch.setattr(
        ctx.__class__,
        "get_ocr_guide_path",
        lambda self, _coll: guide_path,
        raising=False,
    )
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert tab._guide_image.isHidden() is False


def test_set_active_collection_re_evaluates_state(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Cambiar de collection refresca el estado."""
    ctx, coll = ctx_and_collection
    # Empezamos sin factory (Estado No-Model). Al setear la factory y
    # re-llamar set_active_collection, la tab debe transicionar a Ready.
    state = {"has_service": False}
    monkeypatch.setattr(
        ctx.__class__,
        "get_ocr_service",
        lambda self, _coll: object() if state["has_service"] else None,
        raising=False,
    )
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert tab._stack.currentIndex() == _PAGE_NO_MODEL

    state["has_service"] = True
    tab.set_active_collection(coll)
    assert tab._stack.currentIndex() == _PAGE_READY


def test_card_changed_signal_exists(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """El wrapper LoaderTab necesita re-emitir este signal."""
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
# Flow Estado Ready — dispatching del diálogo
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


def _ready_tab(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> tuple[OcrLoaderTab, AppContext, Collection]:
    """Construye una tab en estado Ready para los tests del flow."""
    monkeypatch.setattr(
        ctx_and_collection[0].__class__,
        "get_ocr_service",
        lambda self, _coll: object(),
        raising=False,
    )
    ctx, coll = ctx_and_collection
    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    return tab, ctx, coll


def test_inference_finished_opens_dialog_and_applies_on_accept(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    """Al terminar inferencia se abre el diálogo; si vuelve Accepted, aplica."""
    from PySide6.QtWidgets import QDialog

    tab, _, _ = _ready_tab(qtbot, monkeypatch, ctx_and_collection)

    # Seteamos pending_paths para que _on_inference_finished encuentre la foto.
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    tab._pending_paths = [image]
    tab._current_index = 0

    d_known = _make_detection(card_id=42)
    captured: dict[str, object] = {}

    class _FakeDialog:
        def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
            captured["init_kwargs"] = kwargs
            self.skip = False
            self.cancel_all = False

        def exec(self):  # type: ignore[no-untyped-def]
            return QDialog.DialogCode.Accepted

        def selected_detections(self):  # type: ignore[no-untyped-def]
            return [d_known]

    monkeypatch.setattr(
        "collections_app.views.inventory.ocr_loader_tab.OcrResultDialog",
        _FakeDialog,
    )
    applied: list[tuple[int, str, int, int]] = []
    monkeypatch.setattr(
        tab._ctx.inventory.__class__,
        "add_card",
        lambda self, cid, code, num, qty: applied.append((cid, code, num, qty)),
    )
    # `_process_next_photo` reentraría al flow real; lo neutralizamos —
    # solo queremos verificar el dispatch del primer diálogo.
    monkeypatch.setattr(tab, "_process_next_photo", lambda: None)

    tab._on_inference_finished([d_known], [])

    assert captured["init_kwargs"]["image_path"] == image  # type: ignore[index]
    assert len(applied) == 1
    assert tab._current_index == 1
    assert tab._loaded_count == 1


def test_inference_finished_skip_advances_without_applying(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    """`skip=True`: avanza el índice, NO toca inventario."""
    tab, _, _ = _ready_tab(qtbot, monkeypatch, ctx_and_collection)
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    tab._pending_paths = [image]
    tab._current_index = 0

    class _FakeDialog:
        def __init__(self, **_):  # type: ignore[no-untyped-def]
            self.skip = True
            self.cancel_all = False

        def exec(self):  # type: ignore[no-untyped-def]
            return 0

        def selected_detections(self):  # type: ignore[no-untyped-def]
            return []

    monkeypatch.setattr(
        "collections_app.views.inventory.ocr_loader_tab.OcrResultDialog",
        _FakeDialog,
    )
    applied: list[object] = []
    monkeypatch.setattr(
        tab._ctx.inventory.__class__,
        "add_card",
        lambda *a, **k: applied.append((a, k)),
    )
    monkeypatch.setattr(tab, "_process_next_photo", lambda: None)

    tab._on_inference_finished([_make_detection()], [])

    assert applied == []
    assert tab._current_index == 1


def test_inference_finished_cancel_all_short_circuits_to_summary(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    """`cancel_all=True`: llama directamente a `_show_final_summary`."""
    tab, _, _ = _ready_tab(qtbot, monkeypatch, ctx_and_collection)
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    tab._pending_paths = [image, image]  # 2 fotos pendientes
    tab._current_index = 0

    class _FakeDialog:
        def __init__(self, **_):  # type: ignore[no-untyped-def]
            self.skip = False
            self.cancel_all = True

        def exec(self):  # type: ignore[no-untyped-def]
            return 0

        def selected_detections(self):  # type: ignore[no-untyped-def]
            return []

    monkeypatch.setattr(
        "collections_app.views.inventory.ocr_loader_tab.OcrResultDialog",
        _FakeDialog,
    )
    summary_called = {"n": 0}
    monkeypatch.setattr(
        tab,
        "_show_final_summary",
        lambda: summary_called.__setitem__("n", summary_called["n"] + 1),
    )
    next_called = {"n": 0}
    monkeypatch.setattr(
        tab,
        "_process_next_photo",
        lambda: next_called.__setitem__("n", next_called["n"] + 1),
    )

    tab._on_inference_finished([_make_detection()], [])

    assert summary_called["n"] == 1
    assert next_called["n"] == 0  # no se procesa la siguiente foto
    # _current_index queda en 0 — el short-circuit no avanza.
    assert tab._current_index == 0


def test_apply_detections_skips_unknown_card_id(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """`card_id=None` no se imputa al inventario aunque venga seleccionada."""
    tab, _, _ = _ready_tab(qtbot, monkeypatch, ctx_and_collection)
    calls: list[tuple] = []
    monkeypatch.setattr(
        tab._ctx.inventory.__class__,
        "add_card",
        lambda self, cid, code, num, qty: calls.append((cid, code, num, qty)),
    )
    selected = [
        _make_detection(card_id=42),
        _make_detection(card_id=None, card_name=""),
        _make_detection(card_id=99, card_number=7),
    ]
    tab._apply_detections(selected)

    # Solo las dos con card_id concreto se imputan.
    assert len(calls) == 2


# =====================================================================
# Estado 2 — sub-variantes (Variante A: sin modelo, Variante B: descargar)
# =====================================================================


def _make_collection_with_model_filename(ctx: AppContext, model_filename: str | None) -> Collection:
    """Crea una collection nueva con el `ocr_model_filename` dado."""
    h = ctx.code_headers.create(
        CodeHeader(code_header_id=None, code_header_name="W2", code_max_length=3)
    )
    assert h.code_header_id is not None
    return ctx.collections.create(
        Collection(
            collection_id=None,
            collection_name="Variante",
            card_count=0,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
            ocr_model_filename=model_filename,
        )
    )


def test_state_no_model_variant_b_shows_download_button_when_model_missing(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Modelo configurado en DB pero archivo no existe → botón "Descargar"."""
    ctx, _ = ctx_and_collection
    coll = _make_collection_with_model_filename(ctx, "ocr_1.pt")
    # ctx.get_ocr_service → None (modelo no cargable).
    monkeypatch.setattr(
        ctx.__class__,
        "get_ocr_service",
        lambda self, _coll: None,
        raising=False,
    )
    # ctx.get_ocr_model_path → None (filename configurado pero archivo no en disco).
    monkeypatch.setattr(
        ctx.__class__,
        "get_ocr_model_path",
        lambda self, _coll: None,
        raising=False,
    )

    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert tab._stack.currentIndex() == _PAGE_NO_MODEL
    assert tab._download_model_btn.isHidden() is False
    assert tab._download_model_btn.isEnabled() is True
    assert "no está descargado" in tab._no_model_label.text()


def test_state_no_model_variant_a_hides_download_button_when_filename_absent(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
) -> None:
    """Sin `ocr_model_filename` en DB → mensaje "pedile al admin", botón oculto."""
    ctx, _ = ctx_and_collection
    coll = _make_collection_with_model_filename(ctx, None)
    monkeypatch.setattr(
        ctx.__class__,
        "get_ocr_service",
        lambda self, _coll: None,
        raising=False,
    )
    monkeypatch.setattr(
        ctx.__class__,
        "get_ocr_model_path",
        lambda self, _coll: None,
        raising=False,
    )

    tab = OcrLoaderTab(ctx=ctx, collection=coll)
    qtbot.addWidget(tab)
    assert tab._stack.currentIndex() == _PAGE_NO_MODEL
    assert tab._download_model_btn.isHidden() is True
    assert "no tiene un modelo" in tab._no_model_label.text()
