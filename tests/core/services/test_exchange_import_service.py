"""Tests del ExchangeImportService — validación + snapshot + warnings."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.code_lines_repo import CodeLinesRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.core.security.exchange_signing import compute_signature
from collections_app.services.exchange_errors import (
    CollectionNotFound,
    InvalidExchangeFile,
    UnsupportedFormatVersion,
)
from collections_app.services.exchange_import_service import (
    ExchangeImportService,
)


@pytest.fixture
def collection_with_cards(db_conn: sqlite3.Connection) -> Collection:
    """Collection 'Mundial 2026' con ARG-1 (Messi) y BRA-7 (Neymar)."""
    headers = CodeHeadersRepository(db_conn)
    lines = CodeLinesRepository(db_conn)
    collections = CollectionsRepository(db_conn)
    cards = CardsRepository(db_conn)

    h = headers.create(CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3))
    assert h.code_header_id is not None
    for code in ("ARG", "BRA"):
        lines.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=h.code_header_id,
                code_id=code,
                code_name=code,
                code_order=1,
            )
        )
    coll = collections.create(
        Collection(
            collection_id=None,
            collection_name="Mundial 2026",
            card_count=2,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    assert coll.collection_id is not None
    for code, num, name in [("ARG", 1, "Messi"), ("BRA", 7, "Neymar")]:
        cards.create(
            Card(
                card_id=None,
                collection_id=coll.collection_id,
                code_id=code,
                card_number=num,
                card_name=name,
            )
        )
    db_conn.commit()
    return coll


def _signed_payload(*, missing: list, duplicates: list, version: int = 1) -> dict:
    """Builder de payload firmado para tests."""
    p = {
        "format": "collections_app_exchange",
        "format_version": version,
        "exported_at": "2026-05-15T14:30:00",
        "exported_by_app_version": "0.2.0",
        "collection": {"name": "Mundial 2026", "card_count": 2},
        "user_label": "PGG",
        "missing": missing,
        "duplicates": duplicates,
    }
    p["signature"] = compute_signature(p)
    return p


def _write_payload(tmp_path: Path, payload: dict) -> Path:
    out = tmp_path / "test.colexchange"
    out.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return out


# ---------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------


def test_valid_file_returns_snapshot_no_warnings(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    payload = _signed_payload(
        missing=[
            {"code_id": "ARG", "card_number": 1, "card_name": "Messi", "needed_quantity": 1},
        ],
        duplicates=[
            {
                "code_id": "BRA",
                "card_number": 7,
                "card_name": "Neymar",
                "available_quantity": 2,
            },
        ],
    )
    path = _write_payload(tmp_path, payload)
    svc = ExchangeImportService(db_conn)
    result = svc.read_from_file(path)
    assert result.snapshot.user_label == "PGG"
    assert result.snapshot.collection_name == "Mundial 2026"
    assert len(result.snapshot.missing) == 1
    assert len(result.snapshot.duplicates) == 1
    assert result.warnings == ()
    assert result.local_collection_id == collection_with_cards.collection_id


# ---------------------------------------------------------------------
# Validaciones de formato y firma
# ---------------------------------------------------------------------


def test_malformed_json_raises_invalid(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    path = tmp_path / "bad.colexchange"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(InvalidExchangeFile, match="JSON malformado"):
        ExchangeImportService(db_conn).read_from_file(path)


def test_wrong_format_field_raises_invalid(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    payload = _signed_payload(missing=[], duplicates=[])
    payload["format"] = "something_else"
    payload["signature"] = compute_signature({k: v for k, v in payload.items() if k != "signature"})
    path = _write_payload(tmp_path, payload)
    with pytest.raises(InvalidExchangeFile, match="no generado por esta aplicación"):
        ExchangeImportService(db_conn).read_from_file(path)


def test_missing_format_version_raises_invalid(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    payload = _signed_payload(missing=[], duplicates=[])
    del payload["format_version"]
    payload["signature"] = compute_signature({k: v for k, v in payload.items() if k != "signature"})
    path = _write_payload(tmp_path, payload)
    with pytest.raises(InvalidExchangeFile, match="format_version"):
        ExchangeImportService(db_conn).read_from_file(path)


def test_format_version_zero_raises_invalid(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    payload = _signed_payload(missing=[], duplicates=[], version=0)
    path = _write_payload(tmp_path, payload)
    with pytest.raises(InvalidExchangeFile, match="format_version"):
        ExchangeImportService(db_conn).read_from_file(path)


def test_future_format_version_raises_unsupported(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    payload = _signed_payload(missing=[], duplicates=[], version=2)
    path = _write_payload(tmp_path, payload)
    with pytest.raises(UnsupportedFormatVersion, match="versión 2"):
        ExchangeImportService(db_conn).read_from_file(path)


def test_tampered_signature_raises_invalid(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    payload = _signed_payload(missing=[], duplicates=[])
    # Cambiar contenido sin re-firmar.
    payload["user_label"] = "OTRA_PERSONA"
    path = _write_payload(tmp_path, payload)
    with pytest.raises(InvalidExchangeFile, match="no generado por esta aplicación"):
        ExchangeImportService(db_conn).read_from_file(path)


def test_missing_signature_raises_invalid(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    payload = _signed_payload(missing=[], duplicates=[])
    del payload["signature"]
    path = _write_payload(tmp_path, payload)
    with pytest.raises(InvalidExchangeFile, match="falta la firma"):
        ExchangeImportService(db_conn).read_from_file(path)


# ---------------------------------------------------------------------
# Resolución de colección local
# ---------------------------------------------------------------------


def test_collection_not_in_db_raises_not_found(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
) -> None:
    """Sin colección sembrada en la DB local → CollectionNotFound."""
    payload = _signed_payload(missing=[], duplicates=[])
    path = _write_payload(tmp_path, payload)
    with pytest.raises(CollectionNotFound, match="Mundial 2026"):
        ExchangeImportService(db_conn).read_from_file(path)


# ---------------------------------------------------------------------
# Warnings de cards inexistentes
# ---------------------------------------------------------------------


def test_unknown_card_in_missing_goes_to_warnings(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    """Card del archivo que no existe local → warning, NO se incluye en snapshot."""
    payload = _signed_payload(
        missing=[
            {"code_id": "ARG", "card_number": 1, "card_name": "Messi", "needed_quantity": 1},
            # Esta no existe en la DB.
            {"code_id": "FRA", "card_number": 99, "card_name": "Mbappé", "needed_quantity": 1},
        ],
        duplicates=[],
    )
    path = _write_payload(tmp_path, payload)
    result = ExchangeImportService(db_conn).read_from_file(path)
    assert len(result.snapshot.missing) == 1  # solo ARG-1
    assert len(result.warnings) == 1
    assert "FRA-99" in result.warnings[0]
    assert "Mbappé" in result.warnings[0]


def test_unknown_card_in_duplicates_goes_to_warnings(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    payload = _signed_payload(
        missing=[],
        duplicates=[
            {
                "code_id": "BRA",
                "card_number": 7,
                "card_name": "Neymar",
                "available_quantity": 2,
            },
            {
                "code_id": "FRA",
                "card_number": 99,
                "card_name": "Mbappé",
                "available_quantity": 1,
            },
        ],
    )
    path = _write_payload(tmp_path, payload)
    result = ExchangeImportService(db_conn).read_from_file(path)
    assert len(result.snapshot.duplicates) == 1
    assert len(result.warnings) == 1
    assert "FRA-99" in result.warnings[0]


def test_warnings_capped_at_50(
    tmp_path: Path,
    db_conn: sqlite3.Connection,
    collection_with_cards: Collection,
) -> None:
    """Más de 50 cards desconocidas → warnings truncado a 50."""
    payload = _signed_payload(
        missing=[
            {"code_id": "FRA", "card_number": i, "card_name": f"X{i}", "needed_quantity": 1}
            for i in range(1, 100)
        ],
        duplicates=[],
    )
    path = _write_payload(tmp_path, payload)
    result = ExchangeImportService(db_conn).read_from_file(path)
    assert len(result.warnings) == 50
