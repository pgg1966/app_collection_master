"""Tests del OcrService — mock del pipeline completo (YOLO + cv2 + EasyOCR + validador).

El service NUNCA carga torch/easyocr/cv2 reales en tests: todos los
imports lazy se interceptan con `sys.modules`. La DB usa un archivo
real en `tmp_path` (no `:memory:`) porque `run_inference` abre su
propia conexión vía `sqlite3.connect(db_path)`.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Any

import pytest

from collections_app.app_context import create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.services.exceptions import OcrModelError
from collections_app.services.ocr_service import OcrService

# ---------------------------------------------------------------------
# is_available()
# ---------------------------------------------------------------------


def test_is_available_returns_false_when_torch_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sin torch en sys.modules ni instalado → False, no rompe."""
    monkeypatch.setitem(sys.modules, "torch", None)
    assert OcrService.is_available() is False


def test_is_available_returns_true_when_all_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si los 4 módulos del pipeline importan, devuelve True."""
    for name in ("torch", "ultralytics", "easyocr", "cv2"):
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
    assert OcrService.is_available() is True


def test_is_available_returns_false_when_easyocr_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """torch/ultralytics OK pero falta easyocr → False (pipeline incompleto)."""
    for name in ("torch", "ultralytics", "cv2"):
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
    monkeypatch.setitem(sys.modules, "easyocr", None)
    assert OcrService.is_available() is False


# ---------------------------------------------------------------------
# Constructor — rechazos antes de tocar YOLO
# ---------------------------------------------------------------------


def test_init_raises_when_path_does_not_exist(tmp_path: Path) -> None:
    missing = tmp_path / "does_not_exist.pt"
    with pytest.raises(OcrModelError, match="no existe"):
        OcrService(missing)


def test_init_raises_when_ultralytics_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = tmp_path / "fake_model.pt"
    f.write_bytes(b"\x00\x00")
    monkeypatch.setitem(sys.modules, "ultralytics", None)
    with pytest.raises(OcrModelError, match="no están instaladas"):
        OcrService(f)


def test_init_raises_when_yolo_loader_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    f = tmp_path / "broken.pt"
    f.write_bytes(b"\x00\x00")

    fake_module = types.ModuleType("ultralytics")

    def boom(_path):  # type: ignore[no-untyped-def]
        raise RuntimeError("incompatible torch version")

    fake_module.YOLO = boom  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "ultralytics", fake_module)
    with pytest.raises(OcrModelError, match="no se pudo cargar"):
        OcrService(f)


# ---------------------------------------------------------------------
# run_inference — pipeline completo mockeado
# ---------------------------------------------------------------------


class _FakeTensor:
    """Mínimo `tensor`-like con `.cpu().numpy()` para xyxy."""

    def __init__(self, arr: Any) -> None:
        self._arr = arr

    def cpu(self) -> _FakeTensor:
        return self

    def numpy(self) -> Any:
        return self._arr


class _FakeScalar:
    def __init__(self, val: float) -> None:
        self._val = val

    def __float__(self) -> float:
        return float(self._val)


class _FakeBox:
    def __init__(self, xyxy: list[int], conf: float) -> None:
        # YOLO devuelve `box.xyxy[0]` con shape (4,), `box.conf[0]` scalar.
        import numpy as np  # noqa: PLC0415

        self.xyxy = [_FakeTensor(np.array(xyxy))]
        self.conf = [_FakeScalar(conf)]


class _FakeYoloResult:
    def __init__(self, boxes: list[_FakeBox]) -> None:
        self.boxes = boxes


class _FakeImage:
    """Stub de `numpy.ndarray` con `.shape` y soporte de slicing."""

    def __init__(self) -> None:
        self.shape = (480, 640, 3)

    def __getitem__(self, _slc: Any) -> _FakeImage:
        return _FakeImage()


def _make_service_with_mock_yolo(tmp_path: Path, *, boxes: list[_FakeBox]) -> OcrService:
    """Construye un OcrService cuyo modelo devuelve `boxes` fijo."""
    f = tmp_path / "fake_model.pt"
    f.write_bytes(b"\x00\x00")

    fake_module = types.ModuleType("ultralytics")

    class FakeYolo:
        def __init__(self, _path: str) -> None:
            pass

        def __call__(self, *_a, **_k):  # type: ignore[no-untyped-def]
            return [_FakeYoloResult(boxes)]

    fake_module.YOLO = FakeYolo  # type: ignore[attr-defined]
    sys.modules["ultralytics"] = fake_module
    return OcrService(f)


def _patch_cv2(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub mínimo de cv2 para evitar cargarlo en tests."""
    fake = types.ModuleType("cv2")
    fake.imread = lambda _p: _FakeImage()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "cv2", fake)


@pytest.fixture
def db_with_collection(tmp_path: Path) -> tuple[str, int]:
    """DB en archivo con migraciones aplicadas + colección + cards seedeadas.

    Retorna `(db_path, collection_id)`. Usar archivo (no `:memory:`)
    para que `sqlite3.connect(db_path)` desde el service vea las
    mismas tablas que el seed.
    """
    db_path = tmp_path / "test.db"
    ctx = create_app_context(db_path)
    try:
        headers = CodeHeadersRepository(ctx.conn)
        lines = CodeLinesRepository(ctx.conn)
        collections = CollectionsRepository(ctx.conn)
        cards = CardsRepository(ctx.conn)
        h = headers.create(
            CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
        )
        assert h.code_header_id is not None
        lines.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=h.code_header_id,
                code_id="KOR",
                code_name="Korea",
                code_order=1,
            )
        )
        coll = collections.create(
            Collection(
                collection_id=None,
                collection_name="Mundial",
                card_count=10,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
            )
        )
        assert coll.collection_id is not None
        for n, name in [(6, "Park Ji-Sung"), (10, "Son Heung-min")]:
            cards.create(
                Card(
                    card_id=None,
                    collection_id=coll.collection_id,
                    code_id="KOR",
                    card_number=n,
                    card_name=name,
                )
            )
        ctx.conn.commit()
        return str(db_path), coll.collection_id
    finally:
        ctx.close()


def test_run_inference_full_pipeline_happy_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    db_with_collection: tuple[str, int],
) -> None:
    """YOLO + EasyOCR + validador resuelven una card real del catálogo."""
    db_path, cid = db_with_collection
    _patch_cv2(monkeypatch)
    # `leer_badge` devuelve "KORG" — el validador lo corrige a "KOR 6".
    monkeypatch.setattr(
        "collections_app.services.ocr_service.leer_badge"
        if False
        else "collections_app.services.ocr_reader.leer_badge",
        lambda _crop: "KORG",
    )

    svc = _make_service_with_mock_yolo(
        tmp_path, boxes=[_FakeBox(xyxy=[10, 10, 100, 60], conf=0.92)]
    )
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    detections, errors = svc.run_inference(image, db_path=db_path, collection_id=cid)

    assert errors == []
    assert len(detections) == 1
    d = detections[0]
    assert (d.code_id, d.card_number) == ("KOR", 6)
    assert d.card_name == "Park Ji-Sung"
    assert d.card_id is not None
    assert d.confidence == pytest.approx(0.92)


def test_run_inference_unrecognized_label_goes_to_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    db_with_collection: tuple[str, int],
) -> None:
    """Si EasyOCR devuelve texto que el validador no matchea → ParseError."""
    db_path, cid = db_with_collection
    _patch_cv2(monkeypatch)
    # "XYZ99" no matchea ningún código del catálogo (solo KOR).
    monkeypatch.setattr("collections_app.services.ocr_reader.leer_badge", lambda _crop: "XYZ99")

    svc = _make_service_with_mock_yolo(
        tmp_path, boxes=[_FakeBox(xyxy=[10, 10, 100, 60], conf=0.85)]
    )
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    detections, errors = svc.run_inference(image, db_path=db_path, collection_id=cid)

    assert detections == []
    assert len(errors) == 1
    assert errors[0].raw_label == "XYZ99"
    assert errors[0].confidence == pytest.approx(0.85)
    assert "no matchea" in errors[0].reason


def test_run_inference_detection_for_unknown_card_keeps_in_detections(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    db_with_collection: tuple[str, int],
) -> None:
    """Código válido + card_number FUERA de catálogo → card_id=None, card_name=''."""
    db_path, cid = db_with_collection
    _patch_cv2(monkeypatch)
    # KOR 5 es válido (KOR max=10 en el catálogo) pero no hay card KOR 5.
    monkeypatch.setattr("collections_app.services.ocr_reader.leer_badge", lambda _crop: "KOR5")

    svc = _make_service_with_mock_yolo(
        tmp_path, boxes=[_FakeBox(xyxy=[10, 10, 100, 60], conf=0.75)]
    )
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    detections, errors = svc.run_inference(image, db_path=db_path, collection_id=cid)

    assert errors == []
    assert len(detections) == 1
    d = detections[0]
    assert (d.code_id, d.card_number) == ("KOR", 5)
    assert d.card_id is None
    assert d.card_name == ""


def test_run_inference_raises_when_image_unreadable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    db_with_collection: tuple[str, int],
) -> None:
    """cv2.imread devuelve None → OcrModelError con path en el mensaje."""
    db_path, cid = db_with_collection
    fake = types.ModuleType("cv2")
    fake.imread = lambda _p: None  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "cv2", fake)

    svc = _make_service_with_mock_yolo(tmp_path, boxes=[])
    image = tmp_path / "no-image.jpg"
    with pytest.raises(OcrModelError, match="no se pudo leer la imagen"):
        svc.run_inference(image, db_path=db_path, collection_id=cid)


def test_run_inference_rejects_unknown_collection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    db_with_collection: tuple[str, int],
) -> None:
    db_path, _cid = db_with_collection
    _patch_cv2(monkeypatch)
    svc = _make_service_with_mock_yolo(tmp_path, boxes=[])
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    with pytest.raises(OcrModelError, match="no existe"):
        svc.run_inference(image, db_path=db_path, collection_id=999_999)


def test_run_inference_handles_multiple_boxes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    db_with_collection: tuple[str, int],
) -> None:
    """Varias detecciones en la misma foto → varias entradas en `detections`."""
    db_path, cid = db_with_collection
    _patch_cv2(monkeypatch)

    # Alternar la respuesta de leer_badge para cada crop.
    labels = iter(["KORG", "KOR10"])
    monkeypatch.setattr(
        "collections_app.services.ocr_reader.leer_badge",
        lambda _crop: next(labels),
    )

    svc = _make_service_with_mock_yolo(
        tmp_path,
        boxes=[
            _FakeBox(xyxy=[10, 10, 80, 40], conf=0.91),
            _FakeBox(xyxy=[200, 50, 280, 90], conf=0.87),
        ],
    )
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    detections, errors = svc.run_inference(image, db_path=db_path, collection_id=cid)

    assert errors == []
    assert len(detections) == 2
    assert {(d.code_id, d.card_number) for d in detections} == {("KOR", 6), ("KOR", 10)}
