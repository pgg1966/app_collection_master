"""Diagnóstico read-only de codes_headers huérfanos.

Lista los headers que no tienen ninguna colección apuntándolos.
NO modifica la DB.
"""

import os
import sqlite3
from pathlib import Path

db_path = Path(os.environ["APPDATA"]) / "Collections" / "collections_mundial.db"
print(f"DB: {db_path}\n")

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

# Todos los headers
print("=== Todos los headers ===")
for row in conn.execute(
    "SELECT code_header_id, code_header_name, code_max_length "
    "FROM codes_headers ORDER BY code_header_id"
):
    print(
        f"  id={row['code_header_id']:>3}  "
        f"name={row['code_header_name']:<30}  "
        f"max_len={row['code_max_length']}"
    )

# Headers en uso por colecciones
print("\n=== Headers en uso (referenciados por collections) ===")
in_use = list(
    conn.execute(
        "SELECT DISTINCT c.code_header_id, ch.code_header_name "
        "FROM collections c "
        "JOIN codes_headers ch ON ch.code_header_id = c.code_header_id "
        "ORDER BY c.code_header_id"
    )
)
for row in in_use:
    print(f"  id={row['code_header_id']:>3}  name={row['code_header_name']}")

# Headers huérfanos
print("\n=== Headers HUÉRFANOS (ninguna colección los usa) ===")
orphans = list(
    conn.execute("""
    SELECT ch.code_header_id, ch.code_header_name
    FROM codes_headers ch
    LEFT JOIN collections c ON c.code_header_id = ch.code_header_id
    WHERE c.collection_id IS NULL
    ORDER BY ch.code_header_id
""")
)
if not orphans:
    print("  (ninguno)")
else:
    for row in orphans:
        print(f"  id={row['code_header_id']:>3}  name={row['code_header_name']}")

# Para cada huérfano, contar cuántas codes_lines tiene (info, no se borra)
if orphans:
    print("\n=== codes_lines asociadas a cada huérfano ===")
    print("(NOTA: si se borra el header, las lines caen por CASCADE)")
    for row in orphans:
        count = conn.execute(
            "SELECT COUNT(*) FROM codes_lines WHERE code_header_id = ?",
            (row["code_header_id"],),
        ).fetchone()[0]
        print(
            f"  header_id={row['code_header_id']:>3}  "
            f"name={row['code_header_name']:<30}  "
            f"-> {count} líneas"
        )

conn.close()
print("\nOK (read-only, no se modificó nada).")
