"""Tests del CompareView (smoke + flujos clave).

No tocamos QFileDialog (no se puede headless). Para los flujos de
generación e importación, escribimos directamente el archivo y llamamos
los handlers internos (`_run_comparison`, etc.). Los workers se ejecutan
síncrono usando `worker.run()` en el thread del test cuando es necesario.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from collections_app.client.views.compare_view import CompareView
from collections_app.core.models import Card, ExchangeCard, InventoryItem
from collections_app.core.repositories import (
    CardsRepository,
    InventoryRepository,
)
from collections_app.core.services import ExchangeService

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def collection_with_inv(file_db_path):
    """File DB (necesaria porque los workers abren conexiones nuevas).

    Construimos: collection requires_code=True con cards y un inventario
    inicial. Devolvemos (db_path, conn_principal, collection).
    """
    from collections_app.core.db.connection import create_connection
    from collections_app.core.models import CodeHeader, Collection
    from collections_app.core.repositories import (
        CodesHeadersRepository,
        CollectionsRepository,
    )

    conn = create_connection(file_db_path)
    hdr = CodesHeadersRepository(conn).create(
        CodeHeader(code_header_id=None, code_header_name="Test", code_max_length=5)
    )
    col = CollectionsRepository(conn).create(
        Collection(
            collection_id=None,
            collection_name="TestCol",
            card_count=4,
            requires_code=True,
            code_field_name="País",
            code_header_id=hdr.code_header_id,
        )
    )
    cards_repo = CardsRepository(conn)
    cards = [
        Card(col.collection_id, "ARG", 1, "Messi"),
        Card(col.collection_id, "ARG", 2, "Martínez"),
        Card(col.collection_id, "BRA", 1, "Vinícius"),
        Card(col.collection_id, "BRA", 2, "Neymar"),
    ]
    cards_repo.bulk_upsert(cards)
    inv = InventoryRepository(conn)
    inv.upsert(InventoryItem(col.collection_id, "ARG", 2, quantity=2))
    inv.upsert(InventoryItem(col.collection_id, "BRA", 2, quantity=1))
    conn.commit()
    return file_db_path, conn, col


# ----------------------------------------------------------------------
# Smoke
# ----------------------------------------------------------------------


def test_compare_view_constructs_and_disables_actions_initially(qtbot, collection_with_inv):
    db_path, conn, col = collection_with_inv
    view = CompareView(conn, db_path, col)
    qtbot.addWidget(view)
    view.show()
    # Sin comparación cargada los botones de acción están deshabilitados
    assert view._pdf_button.isEnabled() is False
    assert view._exec_button.isEnabled() is False


def test_set_active_collection_clears_state(qtbot, collection_with_inv, tmp_path):
    db_path, conn, col = collection_with_inv
    # Pre-cargar comparación manualmente
    view = CompareView(conn, db_path, col)
    qtbot.addWidget(view)
    # Generar archivo del propio usuario y simular importación del mismo
    # archivo (compare consigo mismo → resultado vacío pero válido).
    out = tmp_path / "self.colexchange"
    ExchangeService(conn).generate_exchange_file(col.collection_id, out)
    view._other_file = ExchangeService(conn).load_exchange_file(out)
    view._run_comparison()

    # Cambiar de colección debe limpiar el estado
    view.set_active_collection(col)
    assert view._comparison is None
    assert view._other_file is None
    assert view._exec_button.isEnabled() is False


# ----------------------------------------------------------------------
# Flujo completo de comparación
# ----------------------------------------------------------------------


def test_compare_two_users_populates_grids_correctly(qtbot, collection_with_inv, tmp_path):
    db_path, conn, col = collection_with_inv
    cid = col.collection_id

    # Usuario 1 (yo): tengo ARG-2 ×2, BRA-2 ×1, no tengo ARG-1 ni BRA-1.
    # Generamos mi snapshot en otro path (que el view ignora — el view
    # genera su propio snapshot al comparar) pero usamos el mismo path
    # como "archivo del otro usuario" tras editar el inventario.

    # Construimos un "otro usuario" con inventario diferente:
    # tiene ARG-1 ×2 (repetida) y BRA-1 ×1 (una sola). Le faltan ARG-2 y BRA-2.
    # Para eso reutilizamos la DB pero generamos manualmente el ExchangeFile.
    from collections_app.core.models import ExchangeFile

    other_file = ExchangeFile(
        app="CollectionsApp",
        version="1.0",
        collection_id=cid,
        collection_name=col.collection_name,
        generated_at="2026-05-04T00:00:00+00:00",
        missing=[
            ExchangeCard("ARG", 2, "Martínez"),  # le falta lo que yo tengo
            ExchangeCard("BRA", 2, "Neymar"),  # le falta lo que yo tengo
        ],
        duplicates=[
            ExchangeCard("ARG", 1, "Messi", 2),  # tiene repetida lo que yo necesito
            ExchangeCard("BRA", 1, "Vinícius", 2),  # tiene repetida lo que yo necesito
        ],
    )
    # Recalculamos su checksum y escribimos al disco para load_exchange_file
    svc = ExchangeService(conn)
    other_file.checksum = svc._compute_checksum(other_file)  # noqa: SLF001
    other_path = tmp_path / "other.colexchange"
    svc._write_file(other_file, other_path)  # noqa: SLF001

    view = CompareView(conn, db_path, col)
    qtbot.addWidget(view)
    view.show()

    # Simular importación (sin pasar por el QFileDialog): cargamos manual
    loaded = ExchangeService(conn).load_exchange_file(other_path)
    view._other_file = loaded
    view._run_comparison()

    # i_need: ARG-1 y BRA-1 (mis faltantes que el otro tiene repetidas)
    # i_can_offer: ARG-2 (qty=2 → repetida) — BRA-2 tengo qty=1, no es repetida
    assert view._comparison is not None
    need_codes = {(c.code_id, c.card_number) for c in view._comparison.i_need}
    offer_codes = {(c.code_id, c.card_number) for c in view._comparison.i_can_offer}
    assert need_codes == {("ARG", 1), ("BRA", 1)}
    assert offer_codes == {("ARG", 2)}

    # Las grillas reflejan el resultado
    assert view._i_need_list.count() == 2
    assert view._i_offer_list.count() == 1
    # Botones habilitados ahora que hay comparación
    assert view._pdf_button.isEnabled() is True
    assert view._exec_button.isEnabled() is True


def test_import_rejects_different_collection(qtbot, collection_with_inv, tmp_path, monkeypatch):
    """Si el archivo del otro usuario es de otra colección, mostrar warning."""
    db_path, conn, col = collection_with_inv
    from collections_app.core.models import ExchangeFile

    # Archivo de OTRA colección
    other_file = ExchangeFile(
        app="CollectionsApp",
        version="1.0",
        collection_id=999,  # ← distinta a la activa
        collection_name="Otra",
        generated_at="2026-05-04T00:00:00+00:00",
    )
    svc = ExchangeService(conn)
    other_file.checksum = svc._compute_checksum(other_file)  # noqa: SLF001
    path = tmp_path / "wrong.colexchange"
    svc._write_file(other_file, path)  # noqa: SLF001

    view = CompareView(conn, db_path, col)
    qtbot.addWidget(view)
    view.show()

    # Mockear QFileDialog y QMessageBox para no abrir UI
    from PySide6.QtWidgets import QFileDialog, QMessageBox

    monkeypatch.setattr(
        QFileDialog, "getOpenFileName", staticmethod(lambda *a, **kw: (str(path), ""))
    )
    captured = {}

    def fake_warning(parent, title, text):
        captured["title"] = title
        captured["text"] = text
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "warning", staticmethod(fake_warning))

    view._on_import_file()

    assert "Colección distinta" in captured.get("title", "")
    assert view._other_file is None  # no se cargó


def test_import_rejects_invalid_checksum(qtbot, collection_with_inv, tmp_path, monkeypatch):
    """Archivo con checksum inválido: warning + no se carga."""
    db_path, conn, col = collection_with_inv
    import json

    # Generar archivo válido y luego corromperlo
    out = tmp_path / "tampered.colexchange"
    ExchangeService(conn).generate_exchange_file(col.collection_id, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    data["duplicates"].append(
        {"code_id": "FAKE", "card_number": 999, "card_name": "Hacked", "quantity": 5}
    )
    out.write_text(json.dumps(data), encoding="utf-8")

    view = CompareView(conn, db_path, col)
    qtbot.addWidget(view)
    view.show()

    from PySide6.QtWidgets import QFileDialog, QMessageBox

    monkeypatch.setattr(
        QFileDialog, "getOpenFileName", staticmethod(lambda *a, **kw: (str(out), ""))
    )
    captured = {}

    def fake_warning(parent, title, text):
        captured["title"] = title
        captured["text"] = text
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "warning", staticmethod(fake_warning))

    view._on_import_file()

    assert "Archivo inválido" in captured.get("title", "")
    assert "checksum" in captured.get("text", "").lower()
    assert view._other_file is None
