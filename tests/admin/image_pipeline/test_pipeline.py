"""Tests del ImagePipeline con dependencias mockeadas.

Usan `file_db_path` (DB en archivo) porque el pipeline abre su propia
conexión dentro de `run_batch()` para ser compatible con QThread; eso
descarta `:memory:` (cada conn vería una DB vacía distinta).

El tracking de imágenes ahora vive en la tabla `card_images` (migración
003) en lugar del viejo `_index.json`. Los tests verifican vía repo.
"""

import re
import sqlite3
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest
from PIL import Image

from collections_app.admin.image_pipeline.photo_finder import (
    SOURCE_DUCKDUCKGO,
    SOURCE_GOOGLE,
    SOURCE_PLACEHOLDER,
    SOURCE_WIKIPEDIA,
    PhotoResult,
)
from collections_app.admin.image_pipeline.pipeline import ImagePipeline
from collections_app.core.db.connection import create_connection
from collections_app.core.models import (
    Card,
    CardImage,
    CodeHeader,
    CodeLine,
    Collection,
)
from collections_app.core.repositories import (
    CardImagesRepository,
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


def _player_slug(name: str, code: str) -> str:
    """Replica de `PhotoFinder._player_cache_key` para fixtures."""
    slug = re.sub(r"[^A-Z0-9]", "_", name.upper())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return f"{code.upper()}_{slug}"


def _fake_photo_finder(source: str = SOURCE_DUCKDUCKGO, cache_dir: Path | None = None) -> MagicMock:
    """Mock que retorna un PhotoResult fijo apuntando a un cache_path."""
    cache = cache_dir or Path("/fake/cache")

    def find_photo(player_name: str, country_name: str, country_code: str) -> PhotoResult:
        del country_name
        local = cache / f"{_player_slug(player_name, country_code)}.jpg"
        return PhotoResult(
            player_name=player_name,
            source_url=f"https://example.com/{local.stem}.jpg",
            local_path=local,
            source=source,
            success=True,
        )

    def cached_photo_path(name: str, code: str) -> Path:
        return cache / f"{_player_slug(name, code)}.jpg"

    finder = MagicMock()
    finder.cache_dir = cache
    finder.find_photo.side_effect = find_photo
    finder.cached_photo_path.side_effect = cached_photo_path
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
    cache_dir: Path | None = None,
) -> ImagePipeline:
    saved_paths = saved_paths if saved_paths is not None else []
    return ImagePipeline(
        db_path=db_path,
        collection_id=collection_id,
        photo_finder=_fake_photo_finder(photo_source, cache_dir),
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer(saved_paths),
        output_dir=out_dir,
    )


def _read_card_images(db_path: Path, collection_id: int) -> list[CardImage]:
    """Helper: lee el estado de la tabla `card_images` para asserts."""
    conn = create_connection(db_path)
    try:
        return CardImagesRepository(conn).list_by_collection(collection_id)
    finally:
        conn.close()


# ----------------------------------------------------------------------
# Smoke tests del run_batch
# ----------------------------------------------------------------------


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
# Tests específicos del fix de QThread
# ----------------------------------------------------------------------


def test_pipeline_accepts_db_path_not_connection(setup_collection, tmp_path):
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out")
    assert pipe._db_path == db_path
    assert not hasattr(pipe, "conn")


def test_pipeline_creates_own_connection_in_run(setup_collection, tmp_path):
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
    # La última conexión usada por run_batch debe estar cerrada
    last_conn = captured[-1]
    with pytest.raises(sqlite3.ProgrammingError):
        last_conn.execute("SELECT 1")


# ----------------------------------------------------------------------
# Tracking en card_images (migración 003)
# ----------------------------------------------------------------------


def test_run_batch_records_each_card_in_card_images(setup_collection, tmp_path):
    """Después de run_batch, cada card tiene una fila en card_images."""
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out", photo_source=SOURCE_WIKIPEDIA)
    pipe.run_batch()

    images = _read_card_images(db_path, cid)
    assert len(images) == 5
    for img in images:
        assert img.found_photo is True
        assert img.image_source == SOURCE_WIKIPEDIA
        assert img.image_path and img.image_path.endswith(".png")


def test_placeholder_marks_found_photo_false(setup_collection, tmp_path):
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out", photo_source=SOURCE_PLACEHOLDER)
    pipe.run_batch()
    images = _read_card_images(db_path, cid)
    assert all(img.found_photo is False for img in images)
    assert all(img.image_source == SOURCE_PLACEHOLDER for img in images)


def test_get_placeholder_card_keys_reads_from_db(setup_collection, tmp_path):
    """get_placeholder_card_keys() lee de card_images, no del JSON."""
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out", photo_source=SOURCE_PLACEHOLDER)
    pipe.run_batch()
    keys = pipe.get_placeholder_card_keys()
    assert sorted(keys) == ["ARG-1", "ARG-2", "ARG-3", "BRA-1", "BRA-2"]


def test_get_found_count_and_total_generated(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"

    # 3 ARG con foto real, 2 BRA placeholder (manipulamos manualmente)
    _make_pipeline(db_path, cid, out, photo_source=SOURCE_WIKIPEDIA).run_batch(
        card_keys=["ARG-1", "ARG-2", "ARG-3"]
    )
    _make_pipeline(db_path, cid, out, photo_source=SOURCE_PLACEHOLDER).run_batch(
        card_keys=["BRA-1", "BRA-2"]
    )

    pipe = _make_pipeline(db_path, cid, out)
    assert pipe.get_found_count() == 3
    assert pipe.get_total_generated() == 5


def test_regenerate_placeholders_only_reprocesses_placeholders(setup_collection, tmp_path):
    """regenerate_placeholders procesa sólo cards con found_photo=0."""
    db_path, cid = setup_collection
    out = tmp_path / "out"

    # Primera corrida: todos placeholder
    _make_pipeline(db_path, cid, out, photo_source=SOURCE_PLACEHOLDER).run_batch()

    # Marcar 2 como DDG manualmente en card_images
    conn = create_connection(db_path)
    try:
        repo = CardImagesRepository(conn)
        existing_arg1 = repo.get(cid, "ARG", 1)
        assert existing_arg1 is not None
        repo.upsert(
            CardImage(
                collection_id=cid,
                code_id="ARG",
                card_number=1,
                found_photo=True,
                image_source=SOURCE_DUCKDUCKGO,
                image_path=existing_arg1.image_path,
                generated_at=existing_arg1.generated_at,
            )
        )
        existing_bra1 = repo.get(cid, "BRA", 1)
        assert existing_bra1 is not None
        repo.upsert(
            CardImage(
                collection_id=cid,
                code_id="BRA",
                card_number=1,
                found_photo=True,
                image_source=SOURCE_DUCKDUCKGO,
                image_path=existing_bra1.image_path,
                generated_at=existing_bra1.generated_at,
            )
        )
        conn.commit()
    finally:
        conn.close()

    # Reprocesar placeholders: sólo las 3 que siguen marcadas como tal
    saved_regen: list[Path] = []
    pipe2 = _make_pipeline(db_path, cid, out, saved_regen, SOURCE_DUCKDUCKGO)
    result = pipe2.regenerate_placeholders()

    assert result.total == 3
    saved_keys = sorted(p.stem for p in saved_regen)
    assert saved_keys == ["ARG-2", "ARG-3", "BRA-2"]


def test_regenerate_placeholders_when_none(setup_collection, tmp_path):
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out", photo_source=SOURCE_DUCKDUCKGO)
    pipe.run_batch()
    result = pipe.regenerate_placeholders()
    assert result.total == 0


def test_card_images_persist_across_pipeline_instances(setup_collection, tmp_path):
    """Los registros sobreviven a re-instanciar el pipeline (vivieron en DB)."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    pipe = _make_pipeline(db_path, cid, out, photo_source=SOURCE_WIKIPEDIA)
    pipe.run_batch()

    # Reinstanciar y validar
    pipe2 = _make_pipeline(db_path, cid, out, photo_source=SOURCE_DUCKDUCKGO)
    images = _read_card_images(db_path, cid)
    assert len(images) == 5
    assert all(img.image_source == SOURCE_WIKIPEDIA for img in images)
    assert pipe2.get_found_count() == 5


# ----------------------------------------------------------------------
# Cascade delete via FK (migración 003 + connection.py PRAGMA)
# ----------------------------------------------------------------------


def test_cascade_delete_card_image_when_card_deleted(setup_collection, tmp_path):
    """Si se borra una card, su entry de card_images se borra por FK CASCADE."""
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out", photo_source=SOURCE_DUCKDUCKGO)
    pipe.run_batch()
    assert pipe.get_total_generated() == 5

    conn = create_connection(db_path)
    try:
        conn.execute(
            "DELETE FROM cards WHERE collection_id = ? AND code_id = ? AND card_number = ?",
            (cid, "ARG", 1),
        )
        conn.commit()
    finally:
        conn.close()
    assert pipe.get_total_generated() == 4


# ----------------------------------------------------------------------
# run_google_fill (cuota diaria) y breakdown
# ----------------------------------------------------------------------


def _seed_placeholders(setup_collection, out_dir: Path, n: int = 5) -> ImagePipeline:
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, out_dir, photo_source=SOURCE_PLACEHOLDER)
    pipe.run_batch()
    assert len(pipe.get_placeholder_card_keys()) == n
    return pipe


def _fake_finder_for_cascade(
    cache_dir: Path,
    sources_seq: list[str] | None = None,
) -> MagicMock:
    """Finder simulando la cascada: cada card devuelve un source de la secuencia."""
    finder = MagicMock()
    finder.cache_dir = cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    finder.google_calls_used = 0
    finder.google_quota = 100
    sequence = list(sources_seq or [SOURCE_GOOGLE])
    call_idx = {"n": 0}

    def fake_find_photo(player_name: str, country_name: str, country_code: str) -> PhotoResult:
        del country_name
        idx = call_idx["n"]
        call_idx["n"] += 1
        intended = sequence[idx] if idx < len(sequence) else SOURCE_PLACEHOLDER
        if intended == SOURCE_GOOGLE:
            if finder.google_calls_used >= finder.google_quota:
                intended = SOURCE_PLACEHOLDER
            else:
                finder.google_calls_used += 1
        dest = cache_dir / f"{_player_slug(player_name, country_code)}.jpg"
        arr = np.full((200, 200, 3), 200, dtype=np.uint8)
        cv2.imwrite(str(dest), arr)
        return PhotoResult(player_name, f"https://{intended}/x.jpg", dest, intended, True)

    def cached_photo_path(name: str, code: str) -> Path:
        return cache_dir / f"{_player_slug(name, code)}.jpg"

    finder.find_photo.side_effect = fake_find_photo
    finder.cached_photo_path.side_effect = cached_photo_path
    return finder


def test_google_limit_respected_in_run_google_fill(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    _seed_placeholders(setup_collection, out, n=5)

    finder = _fake_finder_for_cascade(cache, sources_seq=[SOURCE_GOOGLE] * 5)
    pipe = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    result = pipe.run_google_fill(daily_limit=2)

    assert result.google_calls_used == 2
    assert result.google_quota_exhausted is True
    assert result.from_google == 2
    assert result.from_placeholder == 3


def test_google_not_called_beyond_daily_limit(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    _seed_placeholders(setup_collection, out, n=5)

    finder = _fake_finder_for_cascade(cache, sources_seq=[SOURCE_GOOGLE] * 5)
    pipe = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    result = pipe.run_google_fill(daily_limit=99)

    assert result.google_calls_used == 5
    assert result.google_quota_exhausted is False
    assert result.from_google == 5
    assert result.from_placeholder == 0


def test_google_fill_skips_when_no_placeholders(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    pipe = _make_pipeline(db_path, cid, out, photo_source=SOURCE_DUCKDUCKGO)
    pipe.run_batch()

    finder = _fake_finder_for_cascade(cache)
    pipe2 = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    result = pipe2.run_google_fill()
    assert result.total == 0
    finder.find_photo.assert_not_called()


def test_google_fill_breakdown_by_source(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    _seed_placeholders(setup_collection, out, n=5)

    finder = _fake_finder_for_cascade(
        cache,
        sources_seq=[
            SOURCE_WIKIPEDIA,
            SOURCE_WIKIPEDIA,
            SOURCE_DUCKDUCKGO,
            SOURCE_DUCKDUCKGO,
            SOURCE_GOOGLE,
        ],
    )
    pipe = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    result = pipe.run_google_fill()

    assert result.from_wikipedia == 2
    assert result.from_duckduckgo == 2
    assert result.from_google == 1
    assert result.from_placeholder == 0
    assert result.google_calls_used == 1


def test_google_fill_leaves_unrecoverable_as_placeholder(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    _seed_placeholders(setup_collection, out, n=5)

    finder = _fake_finder_for_cascade(
        cache,
        sources_seq=[
            SOURCE_WIKIPEDIA,
            SOURCE_WIKIPEDIA,
            SOURCE_PLACEHOLDER,
            SOURCE_PLACEHOLDER,
            SOURCE_PLACEHOLDER,
        ],
    )
    pipe = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    result = pipe.run_google_fill()

    assert result.from_wikipedia == 2
    assert result.from_placeholder == 3
    assert len(pipe.get_placeholder_card_keys()) == 3


def test_google_fill_updates_card_images_to_actual_source(setup_collection, tmp_path):
    """Cada card actualiza su entry de card_images con la fuente real que la rescató."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    _seed_placeholders(setup_collection, out, n=5)

    finder = _fake_finder_for_cascade(
        cache,
        sources_seq=[
            SOURCE_WIKIPEDIA,
            SOURCE_DUCKDUCKGO,
            SOURCE_GOOGLE,
            SOURCE_GOOGLE,
            SOURCE_PLACEHOLDER,
        ],
    )
    pipe = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    pipe.run_google_fill()

    images = _read_card_images(db_path, cid)
    sources = sorted(img.image_source for img in images)
    assert sources == sorted(
        [SOURCE_WIKIPEDIA, SOURCE_DUCKDUCKGO, SOURCE_GOOGLE, SOURCE_GOOGLE, SOURCE_PLACEHOLDER]
    )


def test_google_fill_resets_counter_at_start(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    _seed_placeholders(setup_collection, out, n=5)

    finder = _fake_finder_for_cascade(cache, sources_seq=[SOURCE_GOOGLE] * 5)
    finder.google_calls_used = 50  # estado pre-existente

    pipe = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    pipe.run_google_fill(daily_limit=10)
    assert finder.google_calls_used == 5
    assert finder.google_quota == 10


# ----------------------------------------------------------------------
# run_resketch
# ----------------------------------------------------------------------


def test_run_resketch_skips_placeholders(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    cache.mkdir(parents=True, exist_ok=True)

    # 2 cards con foto real (DDG), 3 placeholder
    _make_pipeline(db_path, cid, out, photo_source=SOURCE_DUCKDUCKGO).run_batch(
        card_keys=["ARG-1", "BRA-2"]
    )
    _make_pipeline(db_path, cid, out, photo_source=SOURCE_PLACEHOLDER).run_batch(
        card_keys=["ARG-2", "ARG-3", "BRA-1"]
    )

    # Crear los archivos cacheados de las cards no-placeholder
    for name, code in [("Messi", "ARG"), ("Neymar", "BRA")]:
        arr = np.full((200, 200, 3), 200, dtype=np.uint8)
        cv2.imwrite(str(cache / f"{_player_slug(name, code)}.jpg"), arr)

    finder = _fake_photo_finder(SOURCE_DUCKDUCKGO, cache_dir=cache)
    sketch_gen = _fake_sketch_generator()
    saved: list[Path] = []
    pipe2 = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=sketch_gen,
        card_composer=_fake_composer(saved),
        output_dir=out,
    )
    result = pipe2.run_resketch()

    assert result.total == 2
    assert sketch_gen.generate_sketch.call_count == 2
    saved_keys = sorted(p.stem for p in saved)
    assert saved_keys == ["ARG-1", "BRA-2"]


def test_run_resketch_uses_cached_photos(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    cache.mkdir(parents=True, exist_ok=True)

    _make_pipeline(db_path, cid, out, photo_source=SOURCE_DUCKDUCKGO).run_batch()

    name_by_card = [
        ("ARG", 1, "Messi"),
        ("ARG", 2, "Martinez"),
        ("ARG", 3, "Molina"),
        ("BRA", 1, "Vinicius"),
        ("BRA", 2, "Neymar"),
    ]
    for code, _, name in name_by_card:
        arr = np.full((200, 200, 3), 200, dtype=np.uint8)
        cv2.imwrite(str(cache / f"{_player_slug(name, code)}.jpg"), arr)

    finder = _fake_photo_finder(SOURCE_DUCKDUCKGO, cache_dir=cache)
    sketch_gen = _fake_sketch_generator()
    pipe2 = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=sketch_gen,
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    result = pipe2.run_resketch()

    assert result.total == 5
    assert result.succeeded == 5
    # generate_sketch fue invocado con paths que apuntan al cache
    for call in sketch_gen.generate_sketch.call_args_list:
        path_arg = call.args[0]
        assert Path(path_arg).parent == cache


def test_run_resketch_does_not_make_network_requests(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    cache.mkdir(parents=True, exist_ok=True)

    _make_pipeline(db_path, cid, out, photo_source=SOURCE_DUCKDUCKGO).run_batch()

    for code, _, name in [
        ("ARG", 1, "Messi"),
        ("ARG", 2, "Martinez"),
        ("ARG", 3, "Molina"),
        ("BRA", 1, "Vinicius"),
        ("BRA", 2, "Neymar"),
    ]:
        arr = np.full((200, 200, 3), 200, dtype=np.uint8)
        cv2.imwrite(str(cache / f"{_player_slug(name, code)}.jpg"), arr)

    finder = _fake_photo_finder(SOURCE_DUCKDUCKGO, cache_dir=cache)
    pipe2 = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    pipe2.run_resketch()

    finder.find_photo.assert_not_called()


def test_run_resketch_handles_missing_cached_photo(setup_collection, tmp_path):
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    cache.mkdir(parents=True, exist_ok=True)

    _make_pipeline(db_path, cid, out, photo_source=SOURCE_DUCKDUCKGO).run_batch()

    finder = _fake_photo_finder(SOURCE_DUCKDUCKGO, cache_dir=cache)
    pipe2 = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    result = pipe2.run_resketch()
    assert result.total == 5
    assert result.failed == 5
    assert result.succeeded == 0


# ----------------------------------------------------------------------
# Migración legacy: ingesto de _index.json viejo
# ----------------------------------------------------------------------


def test_legacy_index_json_is_ingested_and_renamed(setup_collection, tmp_path):
    """Si hay un `_index.json` viejo, lo ingestamos a card_images y lo renombramos."""
    import json as _json

    db_path, cid = setup_collection
    out = tmp_path / "out"
    out.mkdir(parents=True, exist_ok=True)
    legacy_data = {
        "ARG-1": {"source": SOURCE_DUCKDUCKGO, "url": "x"},
        "ARG-2": {"source": SOURCE_PLACEHOLDER, "url": "y"},
    }
    (out / "_index.json").write_text(_json.dumps(legacy_data), encoding="utf-8")

    pipe = _make_pipeline(db_path, cid, out, photo_source=SOURCE_WIKIPEDIA)
    # Forzar abrir conn (para gatillar el ingest)
    pipe.get_total_generated()

    images = _read_card_images(db_path, cid)
    sources = {f"{img.code_id}-{img.card_number}": img.image_source for img in images}
    assert sources == {"ARG-1": SOURCE_DUCKDUCKGO, "ARG-2": SOURCE_PLACEHOLDER}
    # Y el archivo se renombró a .legacy
    assert not (out / "_index.json").exists()
    assert (out / "_index.json.legacy").exists()
