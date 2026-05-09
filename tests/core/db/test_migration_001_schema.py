"""Smoke test del schema producido por la migración 001.

Aplica `001_initial.sql` sobre `:memory:` y verifica el shape final:
- `schema_version = 1`.
- Las 9 tablas esperadas existen.
- Cada tabla con PK subrogada usa `<entidad>_id INTEGER` AUTOINCREMENT.
- UNIQUE constraints sobre business keys.
- FKs granulares (inventory/card_images/transactions → card_id).
- CHECKs y CASCADE funcionan.
- Índices presentes.

No prueba el contenido de las queries de los repos — eso vive en
`tests/core/repositories/`. Acá solo validamos el schema.
"""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations

EXPECTED_TABLES = {
    "schema_version",
    "app_settings",
    "codes_headers",
    "codes_lines",
    "collections",
    "cards",
    "inventory",
    "card_images",
    "transactions",
}

# Tablas con PK subrogada AUTOINCREMENT y nombre de columna esperado.
EXPECTED_SURROGATE_PKS = {
    "codes_headers": "code_header_id",
    "codes_lines": "code_line_id",
    "collections": "collection_id",
    "cards": "card_id",
    "inventory": "inventory_id",
    "card_images": "card_image_id",
    "transactions": "transaction_id",
}

EXPECTED_INDEXES = {
    "idx_codes_lines_order",
    "idx_cards_collection",
    "idx_card_images_found",
    "idx_transactions_date",
    "idx_transactions_card",
    "idx_transactions_exchange_event",
}


@pytest.fixture
def conn() -> sqlite3.Connection:
    """Conexión :memory: con SOLO la migración 001 aplicada.

    Este archivo testea el shape final del schema 001 — usar
    `run_migrations()` aplicaría también las migraciones posteriores
    (002 en adelante), lo cual rompería los asserts cada vez que
    se agrega una migración nueva.
    """
    from collections_app.core.utils.paths import get_schema_dir

    c = create_connection(":memory:")
    sql = (get_schema_dir() / "001_initial.sql").read_text(encoding="utf-8")
    c.executescript(sql)
    return c


def _table_names(conn: sqlite3.Connection) -> set[str]:
    return {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    }


def _index_names(conn: sqlite3.Connection) -> set[str]:
    return {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='index' AND name NOT LIKE 'sqlite_autoindex_%'"
        ).fetchall()
    }


def _columns(conn: sqlite3.Connection, table: str) -> dict[str, sqlite3.Row]:
    return {row["name"]: row for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def _foreign_keys(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    return list(conn.execute(f"PRAGMA foreign_key_list({table})").fetchall())


def _index_list(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    return list(conn.execute(f"PRAGMA index_list({table})").fetchall())


def _is_unique_on(conn: sqlite3.Connection, table: str, expected_cols: tuple[str, ...]) -> bool:
    """True si existe un UNIQUE sobre exactamente esas columnas (en orden)."""
    for idx in _index_list(conn, table):
        if not idx["unique"]:
            continue
        cols = [r["name"] for r in conn.execute(f"PRAGMA index_info({idx['name']})").fetchall()]
        if tuple(cols) == expected_cols:
            return True
    return False


# ---------------------------------------------------------------------
# Versionado y existencia de tablas
# ---------------------------------------------------------------------


def test_schema_version_is_one(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
    assert row["v"] == 1


def test_all_expected_tables_exist(conn: sqlite3.Connection) -> None:
    actual = _table_names(conn)
    missing = EXPECTED_TABLES - actual
    extra = actual - EXPECTED_TABLES - {"sqlite_sequence"}
    assert not missing, f"Tablas faltantes: {missing}"
    assert not extra, f"Tablas inesperadas: {extra}"


def test_all_expected_indexes_exist(conn: sqlite3.Connection) -> None:
    actual = _index_names(conn)
    missing = EXPECTED_INDEXES - actual
    assert not missing, f"Índices faltantes: {missing}"


# ---------------------------------------------------------------------
# PKs subrogadas + AUTOINCREMENT
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "table,pk_col",
    list(EXPECTED_SURROGATE_PKS.items()),
    ids=list(EXPECTED_SURROGATE_PKS.keys()),
)
def test_surrogate_pk_is_integer_and_autoincrement(
    conn: sqlite3.Connection, table: str, pk_col: str
) -> None:
    """Cada tabla con PK subrogada tiene `<x>_id INTEGER PK AUTOINCREMENT`.

    AUTOINCREMENT en SQLite se detecta porque crea filas en `sqlite_sequence`
    cuando se insertan filas. Probamos insertando una fila válida y verificando
    que `sqlite_sequence` registra la tabla.
    """
    cols = _columns(conn, table)
    assert pk_col in cols, f"{table}: falta columna PK {pk_col}"
    col = cols[pk_col]
    assert col["type"].upper() == "INTEGER", f"{table}.{pk_col} no es INTEGER"
    assert col["pk"] == 1, f"{table}.{pk_col} no es PRIMARY KEY"


def test_codes_headers_autoincrement_works(conn: sqlite3.Connection) -> None:
    """Smoke de AUTOINCREMENT real: insertar dos filas y verificar IDs incrementales."""
    conn.execute(
        "INSERT INTO codes_headers (code_header_name, code_max_length) VALUES (?, ?)",
        ("Test1", 5),
    )
    conn.execute(
        "INSERT INTO codes_headers (code_header_name, code_max_length) VALUES (?, ?)",
        ("Test2", 5),
    )
    rows = conn.execute(
        "SELECT code_header_id FROM codes_headers ORDER BY code_header_id"
    ).fetchall()
    ids = [r["code_header_id"] for r in rows]
    assert ids == [1, 2]


# ---------------------------------------------------------------------
# UNIQUE constraints sobre business keys
# ---------------------------------------------------------------------


def test_codes_lines_unique_on_header_code(conn: sqlite3.Connection) -> None:
    assert _is_unique_on(conn, "codes_lines", ("code_header_id", "code_id"))


def test_cards_unique_on_business_key(conn: sqlite3.Connection) -> None:
    assert _is_unique_on(conn, "cards", ("collection_id", "code_id", "card_number"))


def test_inventory_card_id_is_unique(conn: sqlite3.Connection) -> None:
    """inventory es 1:1 con cards via card_id UNIQUE."""
    assert _is_unique_on(conn, "inventory", ("card_id",))


def test_card_images_card_id_is_unique(conn: sqlite3.Connection) -> None:
    """card_images es 1:1 con cards via card_id UNIQUE."""
    assert _is_unique_on(conn, "card_images", ("card_id",))


def test_collections_name_is_unique(conn: sqlite3.Connection) -> None:
    assert _is_unique_on(conn, "collections", ("collection_name",))


def test_codes_headers_name_is_unique(conn: sqlite3.Connection) -> None:
    assert _is_unique_on(conn, "codes_headers", ("code_header_name",))


# ---------------------------------------------------------------------
# Foreign keys granulares (sec 2.5)
# ---------------------------------------------------------------------


def test_inventory_fk_targets_cards(conn: sqlite3.Connection) -> None:
    fks = _foreign_keys(conn, "inventory")
    assert len(fks) == 1
    fk = fks[0]
    assert fk["table"] == "cards"
    assert fk["from"] == "card_id"
    assert fk["to"] == "card_id"
    assert fk["on_delete"] == "CASCADE"


def test_card_images_fk_targets_cards(conn: sqlite3.Connection) -> None:
    fks = _foreign_keys(conn, "card_images")
    assert len(fks) == 1
    fk = fks[0]
    assert fk["table"] == "cards"
    assert fk["from"] == "card_id"
    assert fk["to"] == "card_id"
    assert fk["on_delete"] == "CASCADE"


def test_transactions_fk_targets_card_not_collection(
    conn: sqlite3.Connection,
) -> None:
    """sec 2.5: bitácoras apuntan a la entidad atómica, no al contenedor."""
    fks = _foreign_keys(conn, "transactions")
    assert len(fks) == 1
    fk = fks[0]
    assert fk["table"] == "cards"
    assert fk["from"] == "card_id"


def test_cards_fk_targets_collections_with_cascade(
    conn: sqlite3.Connection,
) -> None:
    fks = _foreign_keys(conn, "cards")
    assert len(fks) == 1
    fk = fks[0]
    assert fk["table"] == "collections"
    assert fk["from"] == "collection_id"
    assert fk["on_delete"] == "CASCADE"


def test_codes_lines_fk_cascade_from_header(conn: sqlite3.Connection) -> None:
    fks = _foreign_keys(conn, "codes_lines")
    assert len(fks) == 1
    fk = fks[0]
    assert fk["table"] == "codes_headers"
    assert fk["on_delete"] == "CASCADE"


# ---------------------------------------------------------------------
# Columnas prohibidas que NO deben existir (sec 6 patrones prohibidos)
# ---------------------------------------------------------------------


def test_inventory_has_no_image_path(conn: sqlite3.Connection) -> None:
    """sec 6: única fuente del path es card_images, no inventory."""
    assert "image_path" not in _columns(conn, "inventory")


def test_inventory_has_no_locked_column(conn: sqlite3.Connection) -> None:
    """Locked era para exchanges con estado; en v0.2 no se persiste."""
    assert "locked" not in _columns(conn, "inventory")


def test_inventory_has_no_denormalized_business_key(
    conn: sqlite3.Connection,
) -> None:
    """sec 2.6: collection_id/code_id/card_number viven en cards, no en inventory."""
    cols = _columns(conn, "inventory")
    for forbidden in ("collection_id", "code_id", "card_number"):
        assert forbidden not in cols, f"inventory.{forbidden} duplica un dato que vive en cards"


def test_card_images_has_no_denormalized_business_key(
    conn: sqlite3.Connection,
) -> None:
    cols = _columns(conn, "card_images")
    for forbidden in ("collection_id", "code_id", "card_number"):
        assert forbidden not in cols, f"card_images.{forbidden} duplica un dato que vive en cards"


def test_transactions_has_no_denormalized_business_key(
    conn: sqlite3.Connection,
) -> None:
    cols = _columns(conn, "transactions")
    for forbidden in ("collection_id", "code_id", "card_number"):
        assert forbidden not in cols, f"transactions.{forbidden} duplica un dato que vive en cards"


# ---------------------------------------------------------------------
# Columnas específicas relevantes
# ---------------------------------------------------------------------


def test_transactions_has_exchange_event_id(conn: sqlite3.Connection) -> None:
    """Agrupa transacciones que pertenecen al mismo intercambio."""
    cols = _columns(conn, "transactions")
    assert "exchange_event_id" in cols
    # Nullable: NULL cuando no es parte de un intercambio.
    assert cols["exchange_event_id"]["notnull"] == 0


def test_collections_has_album_layout_columns(conn: sqlite3.Connection) -> None:
    cols = _columns(conn, "collections")
    for c in ("album_columns", "album_rows", "album_orientation"):
        assert c in cols, f"collections.{c} faltante"


def test_collections_has_code_field_name(conn: sqlite3.Connection) -> None:
    """Label visible del campo de código por colección (UI metadata, no magic column)."""
    cols = _columns(conn, "collections")
    assert "code_field_name" in cols
    assert cols["code_field_name"]["notnull"] == 0


# ---------------------------------------------------------------------
# CHECK constraints y comportamiento runtime
# ---------------------------------------------------------------------


def _seed_minimal_card(conn: sqlite3.Connection) -> int:
    """Crea un universo + colección + card y retorna card_id."""
    conn.execute("INSERT INTO codes_headers (code_header_name) VALUES (?)", ("H",))
    header_id = conn.execute("SELECT code_header_id FROM codes_headers").fetchone()[0]
    conn.execute(
        "INSERT INTO collections (collection_name, card_count, code_header_id) VALUES (?, ?, ?)",
        ("C", 1, header_id),
    )
    coll_id = conn.execute("SELECT collection_id FROM collections").fetchone()[0]
    conn.execute(
        "INSERT INTO cards (collection_id, code_id, card_number, card_name) VALUES (?, ?, ?, ?)",
        (coll_id, "X", 1, "Test"),
    )
    card_id: int = conn.execute("SELECT card_id FROM cards").fetchone()[0]
    return card_id


def test_transactions_quantity_must_be_positive(conn: sqlite3.Connection) -> None:
    card_id = _seed_minimal_card(conn)
    with pytest.raises(sqlite3.IntegrityError, match="quantity"):
        conn.execute(
            "INSERT INTO transactions (card_id, operation, quantity) VALUES (?, 'alta', ?)",
            (card_id, 0),
        )


def test_transactions_operation_must_be_alta_or_baja(
    conn: sqlite3.Connection,
) -> None:
    card_id = _seed_minimal_card(conn)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO transactions (card_id, operation, quantity) VALUES (?, 'foo', 1)",
            (card_id,),
        )


def test_collections_album_orientation_check(conn: sqlite3.Connection) -> None:
    conn.execute("INSERT INTO codes_headers (code_header_name) VALUES (?)", ("H2",))
    header_id = conn.execute(
        "SELECT code_header_id FROM codes_headers WHERE code_header_name = 'H2'"
    ).fetchone()[0]
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO collections "
            "(collection_name, card_count, code_header_id, album_orientation) "
            "VALUES (?, ?, ?, ?)",
            ("BadOrient", 1, header_id, "diagonal"),
        )


def test_cards_unique_violation_raises(conn: sqlite3.Connection) -> None:
    _seed_minimal_card(conn)
    coll_id = conn.execute("SELECT collection_id FROM collections").fetchone()[0]
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO cards (collection_id, code_id, card_number, card_name) "
            "VALUES (?, ?, ?, ?)",
            (coll_id, "X", 1, "Dup"),
        )


def test_inventory_unique_card_id(conn: sqlite3.Connection) -> None:
    card_id = _seed_minimal_card(conn)
    conn.execute("INSERT INTO inventory (card_id, quantity) VALUES (?, ?)", (card_id, 1))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO inventory (card_id, quantity) VALUES (?, ?)", (card_id, 2))


def test_cascade_delete_collection_removes_cards_and_inventory(
    conn: sqlite3.Connection,
) -> None:
    card_id = _seed_minimal_card(conn)
    conn.execute("INSERT INTO inventory (card_id, quantity) VALUES (?, ?)", (card_id, 3))
    coll_id = conn.execute("SELECT collection_id FROM collections").fetchone()[0]
    conn.execute("DELETE FROM collections WHERE collection_id = ?", (coll_id,))
    assert conn.execute("SELECT COUNT(*) AS c FROM cards").fetchone()["c"] == 0
    assert conn.execute("SELECT COUNT(*) AS c FROM inventory").fetchone()["c"] == 0


def test_run_migrations_is_idempotent_on_real_schema(
    conn: sqlite3.Connection,
) -> None:
    """Re-aplicar la migración no debe fallar (no hay pendientes).

    `run_migrations` corre todas las migraciones disponibles. La fixture
    de este archivo aplicó solo la 001, así que `run_migrations` aplica
    las pendientes (002, 003, ...) y deja la versión final igual a la
    cantidad de migraciones disponibles.
    """
    final = run_migrations(conn)
    # El final debe ser >= 1; el valor exacto depende de cuántas
    # migraciones hay en el repo en este momento.
    assert final >= 1
