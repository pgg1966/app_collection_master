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


def test_inference_worker_opens_its_own_connection(
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    """El worker pide una conn propia al ctx (NO usa la del hilo principal).

    Verifica el patrón:
    1. `ctx.create_worker_connection()` se llama dentro de `run()`.
    2. El `OcrService.run_inference` recibe la conn nueva, NO `ctx.conn`.
    3. La conexión se cierra al final.
    """
    from collections_app.views.inventory.ocr_loader_tab import _InferenceWorker

    ctx, coll = ctx_and_collection
    assert coll.collection_id is not None

    # Stub del factory del ctx + un fake conn que registramos.
    opens: list[bool] = []
    closes: list[object] = []

    class _FakeConn:
        def close(self) -> None:  # type: ignore[no-untyped-def]
            closes.append(self)

    def fake_factory(_self):  # type: ignore[no-untyped-def]
        opens.append(True)
        return _FakeConn()

    monkeypatch.setattr(ctx.__class__, "create_worker_connection", fake_factory, raising=False)

    # Stub del OcrService: capturamos qué conn le llegó.
    received_conn: dict[str, object] = {}

    class _FakeOcr:
        def run_inference(self, _img, *, conn, collection_id):  # type: ignore[no-untyped-def]
            received_conn["conn"] = conn
            received_conn["cid"] = collection_id
            return ([], [])

    image = tmp_path / "x.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    worker = _InferenceWorker(
        ocr_service=_FakeOcr(),  # type: ignore[arg-type]
        image_path=image,
        ctx=ctx,
        collection_id=coll.collection_id,
    )

    finished_payloads: list[tuple[list, list]] = []
    worker.finished.connect(lambda d, e: finished_payloads.append((d, e)))

    worker.run()

    # 1. Pidió una conn al ctx exactamente una vez.
    assert opens == [True]
    # 2. La conn que llegó al run_inference NO es la del hilo principal.
    assert isinstance(received_conn["conn"], _FakeConn)
    assert received_conn["conn"] is not ctx.conn
    # 3. La cerró.
    assert len(closes) == 1
    # 4. Emitió `finished` con listas vacías.
    assert finished_payloads == [([], [])]


def test_inference_worker_closes_connection_on_error(
    monkeypatch: pytest.MonkeyPatch,
    ctx_and_collection: tuple[AppContext, Collection],
    tmp_path,  # type: ignore[no-untyped-def]
) -> None:
    """Si `run_inference` levanta OcrError, la conexión se cierra igual."""
    from collections_app.services.exceptions import OcrModelError
    from collections_app.views.inventory.ocr_loader_tab import _InferenceWorker

    ctx, coll = ctx_and_collection
    assert coll.collection_id is not None

    closes: list[object] = []

    class _FakeConn:
        def close(self) -> None:  # type: ignore[no-untyped-def]
            closes.append(self)

    monkeypatch.setattr(
        ctx.__class__,
        "create_worker_connection",
        lambda _self: _FakeConn(),
        raising=False,
    )

    class _FakeOcr:
        def run_inference(self, *_a, **_k):  # type: ignore[no-untyped-def]
            raise OcrModelError("modelo roto")

    image = tmp_path / "x.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    worker = _InferenceWorker(
        ocr_service=_FakeOcr(),  # type: ignore[arg-type]
        image_path=image,
        ctx=ctx,
        collection_id=coll.collection_id,
    )
    failures: list[str] = []
    worker.failed.connect(lambda msg: failures.append(msg))

    worker.run()

    assert failures == ["modelo roto"]
    # Conn cerrada aunque la inferencia rompió.
    assert len(closes) == 1
