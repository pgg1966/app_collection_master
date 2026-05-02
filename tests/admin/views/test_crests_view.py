"""Tests del CrestsView (admin).

Foco: que la vista NO trate como válidos los archivos en disco que no
superan `is_valid_crest_file` (corruptos / vacíos / truncados de un
intento previo). Cubre los 5 puntos donde la vista decide si un escudo
está disponible.
"""

import importlib
import io
import os

from PIL import Image

from collections_app.admin.views import crests_view as view_mod
from collections_app.admin.views.crests_view import (
    STATUS_NONE,
    STATUS_PLACEHOLDER,
    STATUS_WIKIPEDIA,
    CrestsView,
)
from collections_app.core.models import CodeLine
from collections_app.core.repositories import CodesLinesRepository

# Tamaño chico bajo el umbral (MIN_VALID_FILE_BYTES = 1000).
INVALID_BYTES = b"x" * 50


def _valid_png_bytes() -> bytes:
    """PNG real de 200x200 con ruido (siempre > MIN_VALID_FILE_BYTES)."""
    img = Image.frombytes("RGBA", (200, 200), os.urandom(200 * 200 * 4))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


VALID_BYTES = _valid_png_bytes()


def _redirect_crest_dir(monkeypatch, tmp_path):
    """Hace que get_crest_path apunte a tmp_path en TODOS los call sites.

    `crests_view` importa `get_crest_path` directamente, así que hay que
    parchearlo en ese módulo (no en `core.utils.paths`).
    """
    monkeypatch.setattr(
        "collections_app.admin.views.crests_view.get_crest_path",
        lambda code_id: tmp_path / f"{code_id}.png",
    )


def _seed_lines(memory_db, sample_collection, codes):
    repo = CodesLinesRepository(memory_db)
    hid = sample_collection.code_header_id
    for code in codes:
        repo.upsert(CodeLine(hid, code, code))
    memory_db.commit()


# ----------------------------------------------------------------------
# is_valid_crest_file está exportado en el paquete
# ----------------------------------------------------------------------


def test_is_valid_crest_file_exported():
    """`is_valid_crest_file` debe ser importable desde el paquete crests."""
    pkg = importlib.import_module("collections_app.admin.crests")
    assert hasattr(pkg, "is_valid_crest_file")
    assert "is_valid_crest_file" in pkg.__all__


# ----------------------------------------------------------------------
# FIX 3 — _build_row no setea icono para archivos inválidos
# ----------------------------------------------------------------------


def test_invalid_crest_not_shown_as_icon(qtbot, tmp_path, monkeypatch, memory_db):
    _redirect_crest_dir(monkeypatch, tmp_path)
    (tmp_path / "ARG.png").write_bytes(INVALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    line = CodeLine(code_header_id=1, code_id="ARG", code_name="ARGENTINA")
    icon_item, _code, _name, _status = view._build_row(line)

    # Como el PNG es inválido, no se debe haber seteado icono.
    assert icon_item.icon().isNull() is True


def test_valid_crest_shown_as_icon(qtbot, tmp_path, monkeypatch, memory_db):
    _redirect_crest_dir(monkeypatch, tmp_path)
    (tmp_path / "ARG.png").write_bytes(VALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    line = CodeLine(code_header_id=1, code_id="ARG", code_name="ARGENTINA")
    icon_item, *_ = view._build_row(line)

    assert icon_item.icon().isNull() is False


# ----------------------------------------------------------------------
# FIX 4 — _compute_status reporta STATUS_NONE para archivos inválidos
# ----------------------------------------------------------------------


def test_invalid_crest_shown_as_sin_escudo(qtbot, tmp_path, monkeypatch, memory_db):
    _redirect_crest_dir(monkeypatch, tmp_path)
    path = tmp_path / "ARG.png"
    path.write_bytes(INVALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    assert view._compute_status("ARG", path) == STATUS_NONE


def test_valid_crest_shown_as_wikipedia(qtbot, tmp_path, monkeypatch, memory_db):
    _redirect_crest_dir(monkeypatch, tmp_path)
    path = tmp_path / "ARG.png"
    path.write_bytes(VALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    assert view._compute_status("ARG", path) == STATUS_WIKIPEDIA


def test_special_code_invalid_falls_to_placeholder(qtbot, tmp_path, monkeypatch, memory_db):
    """Un code SPECIAL sin escudo válido reporta STATUS_PLACEHOLDER."""
    _redirect_crest_dir(monkeypatch, tmp_path)
    path = tmp_path / "GBL.png"  # GBL ∈ SPECIAL_CODES
    # Sin archivo en disco
    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    assert view._compute_status("GBL", path) == STATUS_PLACEHOLDER


# ----------------------------------------------------------------------
# FIX 2 — _search_auto incluye archivos inválidos como candidatos
# ----------------------------------------------------------------------


def test_invalid_crest_included_as_candidate_for_search(
    qtbot, tmp_path, monkeypatch, memory_db, sample_collection
):
    """Un archivo inválido en disco no impide que el code_id sea candidato."""
    _redirect_crest_dir(monkeypatch, tmp_path)
    _seed_lines(memory_db, sample_collection, ["ARG", "BRA"])
    # ARG con archivo inválido (corrupto), BRA sin archivo.
    (tmp_path / "ARG.png").write_bytes(INVALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)

    # Capturamos los `codes` con los que se construye el worker en lugar
    # de arrancar un thread real.
    captured: dict[str, list[tuple[str, str]]] = {}

    class _StubWorker:
        progress = type("S", (), {"connect": lambda *a, **k: None})()
        finished_ok = type("S", (), {"connect": lambda *a, **k: None})()
        failed = type("S", (), {"connect": lambda *a, **k: None})()

        def __init__(self, finder, codes, parent=None):
            del finder, parent
            captured["codes"] = codes

        def start(self):
            pass

        def isRunning(self):  # noqa: N802 — mimetiza la API de QThread
            return False

    monkeypatch.setattr(view_mod, "_CrestSearchWorker", _StubWorker)
    # Seleccionar la colección recién creada (combo: 0=placeholder, 1=col).
    view._collection_combo.setCurrentIndex(1)
    view._search_auto()

    code_ids = {c[0] for c in captured["codes"]}
    assert "ARG" in code_ids  # inválido en disco → reincluido
    assert "BRA" in code_ids  # sin archivo → incluido


def test_valid_crest_excluded_from_search_candidates(
    qtbot, tmp_path, monkeypatch, memory_db, sample_collection
):
    """Un escudo válido en disco no debe re-procesarse."""
    _redirect_crest_dir(monkeypatch, tmp_path)
    _seed_lines(memory_db, sample_collection, ["ARG", "BRA"])
    (tmp_path / "ARG.png").write_bytes(VALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)

    captured: dict[str, list[tuple[str, str]]] = {}

    class _StubWorker:
        progress = type("S", (), {"connect": lambda *a, **k: None})()
        finished_ok = type("S", (), {"connect": lambda *a, **k: None})()
        failed = type("S", (), {"connect": lambda *a, **k: None})()

        def __init__(self, finder, codes, parent=None):
            del finder, parent
            captured["codes"] = codes

        def start(self):
            pass

        def isRunning(self):  # noqa: N802 — mimetiza la API de QThread
            return False

    monkeypatch.setattr(view_mod, "_CrestSearchWorker", _StubWorker)
    view._collection_combo.setCurrentIndex(1)
    view._search_auto()

    code_ids = {c[0] for c in captured["codes"]}
    assert "ARG" not in code_ids
    assert "BRA" in code_ids


# ----------------------------------------------------------------------
# FIX 6 — _refresh_grid limpia archivos inválidos pre-existentes
# ----------------------------------------------------------------------


def test_refresh_grid_cleans_invalid_files(
    qtbot, tmp_path, monkeypatch, memory_db, sample_collection
):
    """Al refrescar la grilla los archivos inválidos en disco se eliminan."""
    _redirect_crest_dir(monkeypatch, tmp_path)
    _seed_lines(memory_db, sample_collection, ["ARG", "BRA"])
    invalid = tmp_path / "ARG.png"
    valid = tmp_path / "BRA.png"
    invalid.write_bytes(INVALID_BYTES)
    valid.write_bytes(VALID_BYTES)

    view = CrestsView(memory_db)
    qtbot.addWidget(view)
    assert sample_collection.collection_id is not None
    view._refresh_grid(sample_collection.collection_id)

    assert not invalid.exists(), "El archivo inválido debió ser eliminado"
    assert valid.exists(), "El archivo válido NO debe tocarse"
