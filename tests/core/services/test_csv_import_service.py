"""Tests del CsvImportService — codes, cards y facade orquestadora.

Los CSVs son sintéticos (escritos a `tmp_path` por cada test). Las
filas inválidas se acumulan en `errors[]`; las válidas llegan a la DB
vía services existentes (CodeLinesService / CardsService) — los repos
NO se tocan directamente, así que las domain errors se traducen
automáticamente.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from collections_app.core.models.aggregates.csv_import_report import (
    CsvImportReport,
)
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.services.csv_import_service import CsvImportService
from collections_app.services.exceptions import (
    CodeHeadersError,
    CollectionsError,
)


@pytest.fixture
def service(db_conn: sqlite3.Connection) -> CsvImportService:
    return CsvImportService(db_conn)


def _write_csv(path: Path, rows: list[str]) -> None:
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------
# import_codes
# ---------------------------------------------------------------------


def test_import_codes_into_existing_header(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    """Header pre-existente, CSV válido → 3 inserted, 0 skipped."""
    from collections_app.core.repositories.code_headers_repo import (
        CodeHeadersRepository,
    )

    header = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
    )
    db_conn.commit()
    csv_path = tmp_path / "codes.csv"
    _write_csv(
        csv_path,
        [
            "code_id,code_name,code_order",
            "ARG,Argentina,1",
            "BRA,Brasil,2",
            "FRA,Francia,3",
        ],
    )

    report = service.import_codes(csv_path, code_header_name="WC")
    assert isinstance(report, CsvImportReport)
    assert report.rows_total == 3
    assert report.rows_inserted == 3
    assert report.rows_skipped == 0
    assert report.errors == []

    # Verificación: las 3 codes están en la DB.
    assert header.code_header_id is not None
    lines = service._code_lines.list_by_header(header.code_header_id)
    assert {line.code_id for line in lines} == {"ARG", "BRA", "FRA"}


def test_import_codes_is_idempotent(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    """Re-correr el mismo CSV no duplica filas."""
    from collections_app.core.repositories.code_headers_repo import (
        CodeHeadersRepository,
    )

    header = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
    )
    db_conn.commit()
    assert header.code_header_id is not None

    csv_path = tmp_path / "codes.csv"
    _write_csv(
        csv_path,
        [
            "code_id,code_name,code_order",
            "ARG,Argentina,1",
            "BRA,Brasil,2",
        ],
    )

    service.import_codes(csv_path, code_header_name="WC")
    service.import_codes(csv_path, code_header_name="WC")

    lines = service._code_lines.list_by_header(header.code_header_id)
    assert len(lines) == 2  # no duplicados


def test_import_codes_unknown_header_raises(tmp_path: Path, service: CsvImportService) -> None:
    """Header inexistente → CodeHeadersError + nada se importa."""
    csv_path = tmp_path / "codes.csv"
    _write_csv(csv_path, ["code_id,code_name,code_order", "ARG,Argentina,1"])
    with pytest.raises(CodeHeadersError, match="WC"):
        service.import_codes(csv_path, code_header_name="WC")


def test_import_codes_invalid_rows_skipped(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    """Filas inválidas se reportan en errors; las válidas siguen importándose."""
    from collections_app.core.repositories.code_headers_repo import (
        CodeHeadersRepository,
    )

    CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
    )
    db_conn.commit()

    csv_path = tmp_path / "codes.csv"
    _write_csv(
        csv_path,
        [
            "code_id,code_name,code_order",
            "ARG,Argentina,1",
            ",Vacio,2",  # code_id vacío
            "TOOLONG,Largo,3",  # excede max_length=3
            "BRA,,4",  # code_name vacío
            "FRA,Francia,abc",  # code_order no entero
            "ITA,Italia,5",
        ],
    )

    report = service.import_codes(csv_path, code_header_name="WC")
    assert report.rows_total == 6
    assert report.rows_inserted == 2  # ARG, ITA
    assert report.rows_skipped == 4
    assert len(report.errors) == 4
    # row_index 1-based, sin contar header → ARG=1, vacio=2, etc.
    assert {e.row_index for e in report.errors} == {2, 3, 4, 5}


def test_import_codes_no_header_in_csv_uses_positional_order(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    """Sin header en el CSV, asume orden posicional code_id, code_name, code_order."""
    from collections_app.core.repositories.code_headers_repo import (
        CodeHeadersRepository,
    )

    CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
    )
    db_conn.commit()

    csv_path = tmp_path / "codes_noheader.csv"
    _write_csv(csv_path, ["ARG,Argentina,1", "BRA,Brasil,2"])
    report = service.import_codes(csv_path, code_header_name="WC")
    assert report.rows_total == 2
    assert report.rows_inserted == 2


# ---------------------------------------------------------------------
# import_cards
# ---------------------------------------------------------------------


def _seed_collection_with_codes(db_conn: sqlite3.Connection, codes: list[str]) -> int:
    """Helper: header + collection + codes_lines. Retorna collection_id."""
    from collections_app.core.models.code_line import CodeLine
    from collections_app.core.repositories.code_headers_repo import (
        CodeHeadersRepository,
    )
    from collections_app.core.repositories.code_lines_repo import (
        CodeLinesRepository,
    )
    from collections_app.core.repositories.collections_repo import (
        CollectionsRepository,
    )

    h = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="WC", code_max_length=3)
    )
    assert h.code_header_id is not None
    lines = CodeLinesRepository(db_conn)
    for order, code_id in enumerate(codes, start=1):
        lines.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=h.code_header_id,
                code_id=code_id,
                code_name=code_id.lower(),
                code_order=order,
            )
        )
    coll = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="WC2026",
            card_count=0,
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    db_conn.commit()
    assert coll.collection_id is not None
    return coll.collection_id


def test_import_cards_into_existing_collection(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    cid = _seed_collection_with_codes(db_conn, ["ARG", "BRA"])
    csv_path = tmp_path / "cards.csv"
    _write_csv(
        csv_path,
        [
            "code_id,card_number,card_name",
            "ARG,1,Messi",
            "ARG,2,Di Maria",
            "BRA,1,Vinicius",
        ],
    )
    report = service.import_cards(csv_path, collection_name="WC2026")
    assert report.rows_total == 3
    assert report.rows_inserted == 3
    assert report.rows_skipped == 0
    cards = service._cards.list_by_collection(cid)
    assert len(cards) == 3


def test_import_cards_unknown_collection_raises(tmp_path: Path, service: CsvImportService) -> None:
    csv_path = tmp_path / "cards.csv"
    _write_csv(csv_path, ["code_id,card_number,card_name", "ARG,1,Messi"])
    with pytest.raises(CollectionsError, match="WC2026"):
        service.import_cards(csv_path, collection_name="WC2026")


def test_import_cards_unknown_code_id_skipped(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    """Un code_id que no está en codes_lines del header falla por fila."""
    _seed_collection_with_codes(db_conn, ["ARG"])
    csv_path = tmp_path / "cards.csv"
    _write_csv(
        csv_path,
        [
            "code_id,card_number,card_name",
            "ARG,1,Messi",
            "XXX,2,Ghost",  # XXX no existe
        ],
    )
    report = service.import_cards(csv_path, collection_name="WC2026")
    assert report.rows_total == 2
    assert report.rows_inserted == 1
    assert report.rows_skipped == 1
    assert "XXX" in report.errors[0].message


def test_import_cards_invalid_card_number_skipped(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    _seed_collection_with_codes(db_conn, ["ARG"])
    csv_path = tmp_path / "cards.csv"
    _write_csv(
        csv_path,
        [
            "code_id,card_number,card_name",
            "ARG,abc,Messi",  # número no entero
            "ARG,0,Cero",  # 0 no es positivo
            "ARG,-1,Negativo",  # negativo
            "ARG,5,Valida",
        ],
    )
    report = service.import_cards(csv_path, collection_name="WC2026")
    assert report.rows_total == 4
    assert report.rows_inserted == 1
    assert report.rows_skipped == 3


def test_import_cards_empty_name_skipped(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    _seed_collection_with_codes(db_conn, ["ARG"])
    csv_path = tmp_path / "cards.csv"
    _write_csv(
        csv_path,
        [
            "code_id,card_number,card_name",
            "ARG,1,",  # name vacío
            "ARG,2,Valida",
        ],
    )
    report = service.import_cards(csv_path, collection_name="WC2026")
    assert report.rows_inserted == 1
    assert report.rows_skipped == 1


def test_import_cards_is_idempotent(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    cid = _seed_collection_with_codes(db_conn, ["ARG"])
    csv_path = tmp_path / "cards.csv"
    _write_csv(
        csv_path,
        ["code_id,card_number,card_name", "ARG,1,Messi", "ARG,2,DiMaria"],
    )
    service.import_cards(csv_path, collection_name="WC2026")
    service.import_cards(csv_path, collection_name="WC2026")
    cards = service._cards.list_by_collection(cid)
    assert len(cards) == 2


def test_import_cards_rolls_back_on_catastrophic_failure(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Si bulk_upsert lanza, ninguna card se persiste (atomicidad)."""
    cid = _seed_collection_with_codes(db_conn, ["ARG"])
    csv_path = tmp_path / "cards.csv"
    _write_csv(
        csv_path,
        ["code_id,card_number,card_name", "ARG,1,Messi", "ARG,2,DiMaria"],
    )

    def boom(_cards: list) -> int:  # type: ignore[type-arg]
        raise RuntimeError("simulated catastrophic write failure")

    monkeypatch.setattr(service._cards, "bulk_upsert", boom)
    with pytest.raises(RuntimeError, match="simulated"):
        service.import_cards(csv_path, collection_name="WC2026")
    # Ninguna card persistida.
    assert service._cards.count(cid) == 0


# ---------------------------------------------------------------------
# import_collection_from_csvs (facade)
# ---------------------------------------------------------------------


def test_facade_creates_header_and_collection_when_missing(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    codes_csv = tmp_path / "codes.csv"
    cards_csv = tmp_path / "cards.csv"
    _write_csv(
        codes_csv,
        [
            "code_id,code_name,code_order",
            "ARG,Argentina,1",
            "BRA,Brasil,2",
        ],
    )
    _write_csv(
        cards_csv,
        [
            "code_id,card_number,card_name",
            "ARG,1,Messi",
            "BRA,1,Vinicius",
        ],
    )

    reports = service.import_collection_from_csvs(
        collection_name="WC2026",
        code_header_name="WC",
        code_field_name="País",
        code_max_length=3,
        requires_code=True,
        codes_csv_path=codes_csv,
        cards_csv_path=cards_csv,
    )

    assert "codes" in reports
    assert "cards" in reports
    assert reports["codes"].rows_inserted == 2
    assert reports["cards"].rows_inserted == 2

    # Header y Collection creados.
    coll = service._collections.get_by_name("WC2026")
    assert coll is not None
    header = service._code_headers.get_by_name("WC")
    assert header is not None


def test_facade_reuses_existing_targets(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    """Si header + collection ya existen, NO falla — reusa."""
    _seed_collection_with_codes(db_conn, ["ARG"])
    codes_csv = tmp_path / "codes.csv"
    cards_csv = tmp_path / "cards.csv"
    _write_csv(codes_csv, ["code_id,code_name,code_order", "BRA,Brasil,2"])
    _write_csv(cards_csv, ["code_id,card_number,card_name", "ARG,1,Messi", "BRA,1,Vini"])
    reports = service.import_collection_from_csvs(
        collection_name="WC2026",
        code_header_name="WC",
        code_field_name="País",
        code_max_length=3,
        requires_code=True,
        codes_csv_path=codes_csv,
        cards_csv_path=cards_csv,
    )
    assert reports["codes"].rows_inserted == 1  # solo BRA es nuevo
    assert reports["cards"].rows_inserted == 2


def test_facade_with_only_codes_csv(
    tmp_path: Path,
    service: CsvImportService,
) -> None:
    codes_csv = tmp_path / "codes.csv"
    _write_csv(codes_csv, ["code_id,code_name,code_order", "ARG,Argentina,1"])
    reports = service.import_collection_from_csvs(
        collection_name="WC2026",
        code_header_name="WC",
        code_field_name="País",
        code_max_length=3,
        requires_code=True,
        codes_csv_path=codes_csv,
        cards_csv_path=None,
    )
    assert reports["codes"].rows_inserted == 1
    assert "cards" not in reports


def test_facade_with_only_cards_csv(
    tmp_path: Path,
    service: CsvImportService,
    db_conn: sqlite3.Connection,
) -> None:
    """Cards-only requiere que header y codes ya estén creados."""
    _seed_collection_with_codes(db_conn, ["ARG"])
    cards_csv = tmp_path / "cards.csv"
    _write_csv(cards_csv, ["code_id,card_number,card_name", "ARG,1,Messi"])
    reports = service.import_collection_from_csvs(
        collection_name="WC2026",
        code_header_name="WC",
        code_field_name="País",
        code_max_length=3,
        requires_code=True,
        codes_csv_path=None,
        cards_csv_path=cards_csv,
    )
    assert "codes" not in reports
    assert reports["cards"].rows_inserted == 1
