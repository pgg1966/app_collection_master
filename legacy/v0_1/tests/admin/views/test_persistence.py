"""Tests de regresión para garantizar que los saves/deletes de las views
hacen commit a la DB y son visibles desde una conexión fresca.

Estos tests existen como guardrail tras un bug observado donde un combo
no veía cambios "en vivo" entre tabs. La causa real era de visibilidad
en runtime (combo construido una vez), pero estos tests blindan también
el escenario de "abrir la DB con otra conn y ver los cambios", para que
si alguna vez se omite un `conn.commit()` en una view se detecte de inmediato.
"""

from pathlib import Path

from PySide6.QtCore import Qt

from collections_app.admin.views.cards_abm import CardsAbmView
from collections_app.admin.views.codes_master_detail import CodesMasterDetailView
from collections_app.admin.views.collections_abm import CollectionsAbmView
from collections_app.core.db.connection import create_connection
from collections_app.core.models import CodeHeader, CodeLine, Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesHeadersRepository,
    CodesLinesRepository,
    CollectionsRepository,
)


def _read_with_fresh_conn(db_path: Path):
    """Helper: abre una conn nueva al mismo archivo."""
    return create_connection(db_path)


# ----------------------------------------------------------------------
# CodesMasterDetailView — header
# ----------------------------------------------------------------------


def test_save_header_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        view = CodesMasterDetailView(conn)
        qtbot.addWidget(view)
        view.show()

        view.headers_abm._inputs["code_header_name"].setText("Test Header")
        view.headers_abm._inputs["code_max_length"].setValue(5)
        qtbot.mouseClick(view.headers_abm._save_button, Qt.MouseButton.LeftButton)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        rows = fresh.execute("SELECT code_header_name FROM codes_headers").fetchall()
    finally:
        fresh.close()
    names = [r["code_header_name"] for r in rows]
    assert "Test Header" in names


def test_delete_header_persists_to_fresh_conn(qtbot, file_db_path):
    # Pre-poblar con un header
    conn = create_connection(file_db_path)
    try:
        repo = CodesHeadersRepository(conn)
        header = repo.create(CodeHeader(None, "DeleteMe", 5))
        conn.commit()

        view = CodesMasterDetailView(conn)
        qtbot.addWidget(view)
        view.show()
        view.headers_abm.select_record(header)

        # delete via callback directo (evita confirmación modal en tests)
        ok = view._delete_header(header)
        assert ok is True
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        count = fresh.execute("SELECT COUNT(*) AS c FROM codes_headers").fetchone()["c"]
    finally:
        fresh.close()
    assert count == 0


# ----------------------------------------------------------------------
# CodesMasterDetailView — line
# ----------------------------------------------------------------------


def test_save_line_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        header = CodesHeadersRepository(conn).create(CodeHeader(None, "FIFA", 5))
        conn.commit()
        view = CodesMasterDetailView(conn)
        qtbot.addWidget(view)
        view.show()
        view.headers_abm.select_record(header)
        qtbot.wait(50)

        view.lines_abm._inputs["code_id"].setText("ARG")
        view.lines_abm._inputs["code_name"].setText("Argentina")
        view.lines_abm._inputs["code_order"].setValue(1)
        qtbot.mouseClick(view.lines_abm._save_button, Qt.MouseButton.LeftButton)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        rows = fresh.execute("SELECT code_id FROM codes_lines").fetchall()
    finally:
        fresh.close()
    assert any(r["code_id"] == "ARG" for r in rows)


def test_delete_line_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        header = CodesHeadersRepository(conn).create(CodeHeader(None, "FIFA", 5))
        line = CodeLine(header.code_header_id, "ARG", "Argentina")
        CodesLinesRepository(conn).upsert(line)
        conn.commit()

        view = CodesMasterDetailView(conn)
        qtbot.addWidget(view)
        view.show()
        view._current_header = header
        view._delete_line(line)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        count = fresh.execute("SELECT COUNT(*) AS c FROM codes_lines").fetchone()["c"]
    finally:
        fresh.close()
    assert count == 0


# ----------------------------------------------------------------------
# CollectionsAbmView
# ----------------------------------------------------------------------


def test_save_collection_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        # Necesita un header como FK
        header = CodesHeadersRepository(conn).create(CodeHeader(None, "FIFA", 5))
        conn.commit()

        view = CollectionsAbmView(conn)
        qtbot.addWidget(view)
        view.show()

        view.abm._inputs["collection_name"].setText("FIFA WC 2026")
        view.abm._inputs["card_count"].setValue(300)
        view.abm._inputs["code_header_id"].setCurrentIndex(
            view.abm._inputs["code_header_id"].findData(header.code_header_id)
        )
        qtbot.mouseClick(view.abm._save_button, Qt.MouseButton.LeftButton)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        rows = fresh.execute("SELECT collection_name FROM collections").fetchall()
    finally:
        fresh.close()
    names = [r["collection_name"] for r in rows]
    assert "FIFA WC 2026" in names


def test_delete_collection_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        header = CodesHeadersRepository(conn).create(CodeHeader(None, "FIFA", 5))
        col = CollectionsRepository(conn).create(
            Collection(None, "ToDelete", 10, False, None, header.code_header_id)
        )
        conn.commit()

        view = CollectionsAbmView(conn)
        qtbot.addWidget(view)
        view.show()
        view._delete(col)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        count = fresh.execute("SELECT COUNT(*) AS c FROM collections").fetchone()["c"]
    finally:
        fresh.close()
    assert count == 0


# ----------------------------------------------------------------------
# CardsAbmView
# ----------------------------------------------------------------------


def _seed_cards_setup(conn) -> Collection:
    """Crea un header con código + una collection para cards."""
    header = CodesHeadersRepository(conn).create(CodeHeader(None, "FIFA", 5))
    CodesLinesRepository(conn).upsert(CodeLine(header.code_header_id, "ARG", "ARG"))
    col = CollectionsRepository(conn).create(
        Collection(None, "WC", 10, True, "País", header.code_header_id)
    )
    conn.commit()
    return col


def test_save_card_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        col = _seed_cards_setup(conn)

        view = CardsAbmView(conn)
        qtbot.addWidget(view)
        view.show()
        view._on_collection_changed(view._collection_combo.findData(col.collection_id))
        qtbot.wait(50)

        view._cards_widget._inputs["code_id"].setCurrentIndex(0)
        view._cards_widget._inputs["card_number"].setValue(7)
        view._cards_widget._inputs["card_name"].setText("Persisted Card")
        qtbot.mouseClick(view._cards_widget._save_button, Qt.MouseButton.LeftButton)
        qtbot.wait(50)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        rows = fresh.execute("SELECT card_name FROM cards").fetchall()
    finally:
        fresh.close()
    names = [r["card_name"] for r in rows]
    assert "Persisted Card" in names


def test_delete_card_persists_to_fresh_conn(qtbot, file_db_path):
    conn = create_connection(file_db_path)
    try:
        col = _seed_cards_setup(conn)
        from collections_app.core.models import Card

        card = Card(col.collection_id, "ARG", 1, "ToDelete")
        CardsRepository(conn).upsert(card)
        conn.commit()

        view = CardsAbmView(conn)
        qtbot.addWidget(view)
        view.show()
        view._on_collection_changed(view._collection_combo.findData(col.collection_id))
        qtbot.wait(50)
        view._delete_card(card)
    finally:
        conn.close()

    fresh = _read_with_fresh_conn(file_db_path)
    try:
        count = fresh.execute("SELECT COUNT(*) AS c FROM cards").fetchone()["c"]
    finally:
        fresh.close()
    assert count == 0


# ----------------------------------------------------------------------
# E2E: header creado en MasterDetail → visible en CollectionsAbmView combo
# ----------------------------------------------------------------------


def test_header_from_master_detail_visible_in_collections_combo(qtbot, file_db_path):
    """Reproduce el bug original: crear un header en CodesMasterDetailView y
    luego, con la MISMA conn (como hace AdminMainWindow), ver que aparece en el
    combo de CollectionsAbmView al hacer Nuevo, sin reiniciar."""
    conn = create_connection(file_db_path)
    try:
        codes_view = CodesMasterDetailView(conn)
        collections_view = CollectionsAbmView(conn)
        qtbot.addWidget(codes_view)
        qtbot.addWidget(collections_view)
        codes_view.show()
        collections_view.show()

        # Crear un header desde la UI de Cabeceras
        codes_view.headers_abm._inputs["code_header_name"].setText("New Header")
        codes_view.headers_abm._inputs["code_max_length"].setValue(5)
        qtbot.mouseClick(codes_view.headers_abm._save_button, Qt.MouseButton.LeftButton)
        qtbot.wait(50)

        # Ahora simular click en "Nuevo" del ABM de Colecciones
        qtbot.mouseClick(collections_view.abm._new_button, Qt.MouseButton.LeftButton)
        qtbot.wait(50)

        combo = collections_view.abm._inputs["code_header_id"]
        labels = [combo.itemText(i) for i in range(combo.count())]
        assert "New Header" in labels
    finally:
        conn.close()
