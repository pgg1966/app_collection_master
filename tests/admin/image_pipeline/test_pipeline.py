"""Tests del ImagePipeline con dependencias mockeadas.

Usan `file_db_path` (DB en archivo) porque el pipeline abre su propia
conexión dentro de `run_batch()` para ser compatible con QThread; eso
descarta `:memory:` (cada conn vería una DB vacía distinta).
"""

import sqlite3
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PIL import Image

from collections_app.admin.image_pipeline.photo_finder import (
    SOURCE_DUCKDUCKGO,
    SOURCE_PLACEHOLDER,
    SOURCE_WIKIPEDIA,
    PhotoResult,
)
from collections_app.admin.image_pipeline.pipeline import ImagePipeline
from collections_app.core.db.connection import create_connection
from collections_app.core.models import (
    Card,
    CodeHeader,
    CodeLine,
    Collection,
)
from collections_app.core.repositories import (
    CardsRepository,
    CodesHeadersRepository,
    CodesLinesRepository,
    CollectionsRepository,
)


@pytest.fixture
def setup_collection(file_db_path):
    """DB en archivo + colección con 5 cards y 2 codes_lines."""
    conn = create_connection(file_db_path)
    try:
        header = CodesHeadersRepository(conn).create(
            CodeHeader(code_header_id=None, code_header_name="FIFA", code_max_length=5)
        )
        lines = CodesLinesRepository(conn)
        for code, name in [("ARG", "ARGENTINA"), ("BRA", "BRAZIL")]:
            lines.upsert(CodeLine(header.code_header_id, code, name))

        col = CollectionsRepository(conn).create(
            Collection(
                collection_id=None,
                collection_name="Test",
                card_count=5,
                requires_code=True,
                code_field_name="País",
                code_header_id=header.code_header_id,
            )
        )
        cards = CardsRepository(conn)
        cards.upsert(Card(col.collection_id, "ARG", 1, "Messi"))
        cards.upsert(Card(col.collection_id, "ARG", 2, "Martinez"))
        cards.upsert(Card(col.collection_id, "ARG", 3, "Molina"))
        cards.upsert(Card(col.collection_id, "BRA", 1, "Vinicius"))
        cards.upsert(Card(col.collection_id, "BRA", 2, "Neymar"))
        conn.commit()
    finally:
        conn.close()
    return file_db_path, col.collection_id


def _fake_photo_finder(source: str = SOURCE_DUCKDUCKGO) -> MagicMock:
    """Mock que retorna un PhotoResult fijo apuntando a un fake JPG."""

    def find_photo(player_name: str, country_name: str, card_key: str) -> PhotoResult:
        return PhotoResult(
            player_name=player_name,
            source_url=f"https://example.com/{card_key}.jpg",
            local_path=Path("/fake/path.jpg"),
            source=source,
            success=True,
        )

    finder = MagicMock()
    finder.find_photo.side_effect = find_photo
    return finder


def _fake_sketch_generator() -> MagicMock:
    gen = MagicMock()
    gen.generate_sketch.return_value = np.full((310, 260), 200, dtype=np.uint8)
    return gen


def _fake_composer(saved_paths: list[Path]) -> MagicMock:
    composer = MagicMock()
    composer.compose.return_value = Image.new("RGB", (280, 380), (200, 200, 200))

    def save(_image, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.touch()
        saved_paths.append(output_path)

    composer.save.side_effect = save
    return composer


def _make_pipeline(
    db_path: Path,
    collection_id: int,
    out_dir: Path,
    saved_paths: list[Path] | None = None,
    photo_source: str = SOURCE_DUCKDUCKGO,
) -> ImagePipeline:
    saved_paths = saved_paths if saved_paths is not None else []
    return ImagePipeline(
        db_path=db_path,
        collection_id=collection_id,
        photo_finder=_fake_photo_finder(photo_source),
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer(saved_paths),
        output_dir=out_dir,
    )


def test_skips_already_generated_cards(setup_collection, tmp_path):
    db_path, cid = setup_collection
    saved: list[Path] = []
    out = tmp_path / "out"
    pipe = _make_pipeline(db_path, cid, out, saved)
    out.mkdir(exist_ok=True)
    (out / "ARG-1.png").touch()

    result = pipe.run_batch()
    assert result.total == 5
    assert result.succeeded == 5
    assert result.from_cache >= 1
    saved_keys = [p.stem for p in saved]
    assert "ARG-1" not in saved_keys


def test_processes_in_batches(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"
    pipe = _make_pipeline(db_path, cid, out)
    progress: list[tuple[int, int, str]] = []
    result = pipe.run_batch(
        on_progress=lambda c, t, n: progress.append((c, t, n)),
        batch_size=2,
    )
    assert result.total == 5
    assert progress[-1][0] == 5
    assert progress[-1][1] == 5


def test_progress_callback_called_per_card(setup_collection, tmp_path):
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out")
    calls = 0

    def cb(_c: int, _t: int, _n: str) -> None:
        nonlocal calls
        calls += 1

    pipe.run_batch(on_progress=cb)
    assert calls == 5


def test_result_counts_sources_correctly(setup_collection, tmp_path):
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out", photo_source=SOURCE_WIKIPEDIA)
    result = pipe.run_batch()
    assert result.from_wikipedia == 5


def test_stop_signal_halts_after_batch(setup_collection, tmp_path):
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out")

    def cb(c: int, _t: int, _n: str) -> None:
        if c == 2:
            pipe.stop()

    result = pipe.run_batch(on_progress=cb, batch_size=2)
    assert result.succeeded <= 2


def test_force_regenerates_existing(setup_collection, tmp_path):
    db_path, cid = setup_collection
    saved: list[Path] = []
    out = tmp_path / "out"
    pipe = _make_pipeline(db_path, cid, out, saved)
    out.mkdir(exist_ok=True)
    (out / "ARG-1.png").write_bytes(b"old")

    pipe.run_batch(force=True)
    saved_keys = [p.stem for p in saved]
    assert "ARG-1" in saved_keys


def test_placeholder_counted_separately(setup_collection, tmp_path):
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out", photo_source=SOURCE_PLACEHOLDER)
    result = pipe.run_batch()
    assert result.from_placeholder == 5
    assert result.from_duckduckgo == 0


def test_output_dir_created_automatically(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "deep" / "nested" / "out"
    pipe = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=_fake_photo_finder(),
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    pipe.run_batch()
    assert out.exists()


def test_card_keys_filter(setup_collection, tmp_path):
    db_path, cid = setup_collection
    saved: list[Path] = []
    pipe = _make_pipeline(db_path, cid, tmp_path / "out", saved)
    result = pipe.run_batch(card_keys=["ARG-1", "BRA-2"])
    assert result.total == 2
    saved_keys = sorted(p.stem for p in saved)
    assert saved_keys == ["ARG-1", "BRA-2"]


def test_get_existing_count(setup_collection, tmp_path):
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out")
    assert pipe.get_existing_count() == 0
    pipe.run_batch()
    assert pipe.get_existing_count() == 5


def test_unknown_collection_raises(setup_collection, tmp_path):
    db_path, _ = setup_collection
    pipe = ImagePipeline(
        db_path=db_path,
        collection_id=9999,
        photo_finder=_fake_photo_finder(),
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=tmp_path / "out",
    )
    with pytest.raises(ValueError, match="no existe"):
        pipe.run_batch()


# ----------------------------------------------------------------------
# Tests específicos del fix (compatibilidad con QThread)
# ----------------------------------------------------------------------


def test_pipeline_accepts_db_path_not_connection(setup_collection, tmp_path):
    """Regresión: el __init__ acepta db_path (Path), no sqlite3.Connection."""
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out")
    # Guarda el path, no una conexión.
    assert pipe._db_path == db_path
    assert not hasattr(pipe, "conn")


def test_pipeline_creates_own_connection_in_run(setup_collection, tmp_path):
    """El run abre su propia conn → ejecutar el método en otro thread no
    debe lanzar `sqlite3.ProgrammingError: SQLite objects created in a
    thread can only be used in that same thread`."""
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out")
    result_holder: list = []
    error_holder: list = []

    def runner() -> None:
        try:
            result_holder.append(pipe.run_batch())
        except Exception as exc:  # noqa: BLE001
            error_holder.append(exc)

    t = threading.Thread(target=runner)
    t.start()
    t.join(timeout=10)
    assert not error_holder, f"Excepción en thread: {error_holder}"
    assert result_holder, "El thread no completó"
    result = result_holder[0]
    assert result.total == 5
    assert result.succeeded == 5


def test_pipeline_closes_connection_after_run(setup_collection, tmp_path):
    """La conn se cierra al terminar el run (validamos vía spy)."""
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out")

    captured: list[sqlite3.Connection] = []

    def spying_create(path):
        conn = create_connection(path)
        captured.append(conn)
        return conn

    with patch(
        "collections_app.admin.image_pipeline.pipeline.create_connection",
        side_effect=spying_create,
    ):
        pipe.run_batch()

    assert captured, "No se creó ninguna conexión"
    conn = captured[0]
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")
