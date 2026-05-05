"""Tests del script cleanup_orphans."""

import sqlite3

from collections_app.core.db.connection import create_connection
from collections_app.core.db.scripts.cleanup_orphans import cleanup_orphans
from collections_app.core.models import Card, CodeHeader, Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesHeadersRepository,
    CollectionsRepository,
)


def _insert_without_fk(db_path, sql: str, params: tuple = ()) -> None:
    """Inserta una fila bypaseando FK (conexión cruda sin el PRAGMA)."""
    raw = sqlite3.connect(str(db_path))
    try:
        raw.execute(sql, params)
        raw.commit()
    finally:
        raw.close()


def _make_collection(conn, name: str = "C1") -> Collection:
    header = CodesHeadersRepository(conn).create(
        CodeHeader(code_header_id=None, code_header_name=f"H_{name}", code_max_length=5)
    )
    return CollectionsRepository(conn).create(
        Collection(
            collection_id=None,
            collection_name=name,
            card_count=3,
            requires_code=True,
            code_field_name="País",
            code_header_id=header.code_header_id,
        )
    )


def test_cleanup_removes_orphan_cards(file_db_path):
    """Cards apuntando a collection_id que no existe → eliminadas."""
    conn = create_connection(file_db_path)
    try:
        col = _make_collection(conn, "C1")
        cards = CardsRepository(conn)
        cards.upsert(Card(col.collection_id, "ARG", 1, "X"))
        cards.upsert(Card(col.collection_id, "ARG", 2, "Y"))
        conn.commit()
    finally:
        conn.close()

    # Insertar card huérfana sin FK enforcement (simula bug del usuario)
    _insert_without_fk(
        file_db_path,
        "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
        "VALUES (9999, 'ZZZ', 1, 'Orphan')",
    )

    deleted = cleanup_orphans(str(file_db_path))
    assert deleted["cards"] == 1

    # Verificar que las cards reales siguen
    conn = create_connection(file_db_path)
    try:
        n = conn.execute("SELECT COUNT(*) AS n FROM cards").fetchone()["n"]
        assert n == 2
    finally:
        conn.close()


def test_cleanup_removes_orphan_transactions(file_db_path):
    conn = create_connection(file_db_path)
    try:
        col = _make_collection(conn, "C1")
        # transacciones con collection_id válido
        conn.execute(
            "INSERT INTO transactions (collection_id, code_id, card_number, operation, quantity) "
            "VALUES (?, 'ARG', 1, 'alta', 1)",
            (col.collection_id,),
        )
        conn.commit()
    finally:
        conn.close()

    # Transacción huérfana (collection_id no existe)
    _insert_without_fk(
        file_db_path,
        "INSERT INTO transactions (collection_id, code_id, card_number, operation, quantity) "
        "VALUES (9999, 'XX', 1, 'alta', 1)",
    )

    deleted = cleanup_orphans(str(file_db_path))
    assert deleted["transactions"] == 1


def test_cleanup_returns_zero_when_no_orphans(file_db_path):
    """Sin huérfanos, todas las cuentas son 0."""
    conn = create_connection(file_db_path)
    try:
        col = _make_collection(conn, "C1")
        CardsRepository(conn).upsert(Card(col.collection_id, "ARG", 1, "X"))
        conn.commit()
    finally:
        conn.close()

    deleted = cleanup_orphans(str(file_db_path))
    assert all(n == 0 for n in deleted.values())


def test_cleanup_includes_card_images_table(file_db_path):
    """La tabla card_images también se limpia."""
    conn = create_connection(file_db_path)
    try:
        col = _make_collection(conn, "C1")
        CardsRepository(conn).upsert(Card(col.collection_id, "ARG", 1, "X"))
        conn.commit()
    finally:
        conn.close()

    # Entry huérfana en card_images
    _insert_without_fk(
        file_db_path,
        "INSERT INTO card_images (collection_id, code_id, card_number, found_photo) "
        "VALUES (9999, 'XX', 1, 1)",
    )

    deleted = cleanup_orphans(str(file_db_path))
    assert deleted["card_images"] == 1
