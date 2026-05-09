"""Tests del OcrService — mock YOLO para no cargar torch.

Cubre:
- `is_available()`: True/False según si los módulos están en sys.modules.
- Constructor: rechaza paths inválidos (OcrModelError) sin tocar YOLO.
- `run_inference`: mockea `_raw_inference` (capa que toca YOLO) y
  verifica el parseo + resolución contra el catálogo.
"""

from __future__ import annotations

import sqlite3
import sys
import types
from pathlib import Path
from unittest.mock import patch

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.models.ocr_detection import OcrDetection, OcrParseError
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
    # Borrar de sys.modules cualquier import previo y forzar fallo del import.
    monkeypatch.setitem(sys.modules, "torch", None)
    assert OcrService.is_available() is False


def test_is_available_returns_true_when_both_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si ambos módulos importan, devuelve True."""
    fake_torch = types.ModuleType("torch")
    fake_ultralytics = types.ModuleType("ultralytics")
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setitem(sys.modules, "ultralytics", fake_ultralytics)
    assert OcrService.is_available() is True


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
    """Path válido pero ultralytics no importable → OcrModelError."""
    f = tmp_path / "fake_model.pt"
    f.write_bytes(b"\x00\x00")  # archivo presente, contenido irrelevante

    monkeypatch.setitem(sys.modules, "ultralytics", None)
    with pytest.raises(OcrModelError, match="no están instaladas"):
        OcrService(f)


def test_init_raises_when_yolo_loader_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """ultralytics importable, pero YOLO() rompe → OcrModelError."""
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
# run_inference — mockea _raw_inference
# ---------------------------------------------------------------------


def _make_service_with_mock_yolo(tmp_path: Path) -> OcrService:
    """Construye un OcrService con YOLO mockeado para evitar torch."""
    f = tmp_path / "fake_model.pt"
    f.write_bytes(b"\x00\x00")

    fake_module = types.ModuleType("ultralytics")

    class FakeYolo:
        def __init__(self, _path: str) -> None:
            pass

        def __call__(self, *_a, **_k):  # type: ignore[no-untyped-def]
            return []

    fake_module.YOLO = FakeYolo  # type: ignore[attr-defined]
    sys.modules["ultralytics"] = fake_module
    return OcrService(f)


@pytest.fixture
def collection_with_cards(
    db_conn: sqlite3.Connection,
) -> Collection:
    """Header WC + colección con código + 2 cards."""
    headers = CodeHeadersRepository(db_conn)
    lines = CodeLinesRepository(db_conn)
    collections = CollectionsRepository(db_conn)
    cards = CardsRepository(db_conn)

    h = headers.create(CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3))
    assert h.code_header_id is not None
    lines.upsert(
        CodeLine(
            code_line_id=None,
            code_header_id=h.code_header_id,
            code_id="ARG",
            code_name="Argentina",
            code_order=1,
        )
    )
    coll = collections.create(
        Collection(
            collection_id=None,
            collection_name="Mundial",
            card_count=2,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    assert coll.collection_id is not None
    for num, name in [(4, "Lautaro"), (10, "Messi")]:
        cards.create(
            Card(
                card_id=None,
                collection_id=coll.collection_id,
                code_id="ARG",
                card_number=num,
                card_name=name,
            )
        )
    db_conn.commit()
    return coll


def test_run_inference_returns_detection_for_known_card(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    svc = _make_service_with_mock_yolo(tmp_path)
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")  # JPEG magic bytes — no se usa de verdad

    with patch.object(svc, "_raw_inference", return_value=[("ARG-04", 0.94), ("ARG-10", 0.81)]):
        assert collection_with_cards.collection_id is not None
        detections, errors = svc.run_inference(
            image, conn=db_conn, collection_id=collection_with_cards.collection_id
        )

    assert errors == []
    assert len(detections) == 2
    assert detections[0] == OcrDetection(
        raw_label="ARG-04",
        code_id="ARG",
        card_number=4,
        confidence=0.94,
        card_name="Lautaro",
        card_id=detections[0].card_id,  # depende del autoincrement
    )
    assert detections[0].card_id is not None
    assert detections[1].card_name == "Messi"


def test_run_inference_keeps_detection_when_card_not_in_catalog(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    """Card detectada que no existe en la DB local: card_id=None, card_name=''."""
    svc = _make_service_with_mock_yolo(tmp_path)
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")

    with patch.object(svc, "_raw_inference", return_value=[("FRA-99", 0.88)]):
        assert collection_with_cards.collection_id is not None
        detections, errors = svc.run_inference(
            image, conn=db_conn, collection_id=collection_with_cards.collection_id
        )
    assert errors == []
    assert len(detections) == 1
    d = detections[0]
    assert (d.code_id, d.card_number) == ("FRA", 99)
    assert d.card_id is None
    assert d.card_name == ""


def test_run_inference_collects_parse_errors(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    """Labels no parseables → OcrParseError, no rompen el flow."""
    svc = _make_service_with_mock_yolo(tmp_path)
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")

    with patch.object(
        svc,
        "_raw_inference",
        return_value=[
            ("ARG-04", 0.95),  # válida
            ("???", 0.5),  # no parsea
            ("99", 0.3),  # falta código (collection requires_code=True)
        ],
    ):
        assert collection_with_cards.collection_id is not None
        detections, errors = svc.run_inference(
            image, conn=db_conn, collection_id=collection_with_cards.collection_id
        )
    assert len(detections) == 1
    assert detections[0].raw_label == "ARG-04"
    assert len(errors) == 2
    assert all(isinstance(e, OcrParseError) for e in errors)


def test_run_inference_rejects_unknown_collection(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
) -> None:
    svc = _make_service_with_mock_yolo(tmp_path)
    image = tmp_path / "foto.jpg"
    image.write_bytes(b"\xff\xd8\xff")
    with (
        patch.object(svc, "_raw_inference", return_value=[]),
        pytest.raises(OcrModelError, match="no existe"),
    ):
        svc.run_inference(image, conn=db_conn, collection_id=999_999)
