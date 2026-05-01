"""Tests del ImagePipeline con dependencias mockeadas.

Usan `file_db_path` (DB en archivo) porque el pipeline abre su propia
conexión dentro de `run_batch()` para ser compatible con QThread; eso
descarta `:memory:` (cada conn vería una DB vacía distinta).
"""

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


# ----------------------------------------------------------------------
# Mejoras: _index.json y regenerate_placeholders
# ----------------------------------------------------------------------


def test_index_json_records_sources(setup_collection, tmp_path):
    """Tras run_batch, `_index.json` lista las fuentes por card."""
    import json as _json

    db_path, cid = setup_collection
    out = tmp_path / "out"
    pipe = _make_pipeline(db_path, cid, out, photo_source=SOURCE_PLACEHOLDER)
    pipe.run_batch()
    index_path = out / "_index.json"
    assert index_path.exists()
    data = _json.loads(index_path.read_text(encoding="utf-8"))
    assert len(data) == 5
    for entry in data.values():
        assert entry["source"] == SOURCE_PLACEHOLDER


def test_get_placeholder_card_keys_filters_correctly(setup_collection, tmp_path):
    """get_placeholder_card_keys() devuelve solo las cards con source=placeholder."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    pipe = _make_pipeline(db_path, cid, out, photo_source=SOURCE_PLACEHOLDER)
    pipe.run_batch()
    keys = pipe.get_placeholder_card_keys()
    assert sorted(keys) == ["ARG-1", "ARG-2", "ARG-3", "BRA-1", "BRA-2"]

    # Reinstanciar el pipeline (para forzar recarga del index desde disco) y
    # comparar.
    pipe2 = _make_pipeline(db_path, cid, out, photo_source=SOURCE_PLACEHOLDER)
    assert sorted(pipe2.get_placeholder_card_keys()) == sorted(keys)


def test_regenerate_placeholders_only_reprocesses_placeholders(setup_collection, tmp_path):
    """regenerate_placeholders borra solo los PNGs de placeholder y los reprocesa."""
    db_path, cid = setup_collection
    out = tmp_path / "out"

    # Primera corrida: todos como placeholder
    saved_first: list[Path] = []
    pipe = _make_pipeline(db_path, cid, out, saved_first, SOURCE_PLACEHOLDER)
    pipe.run_batch()
    assert len(saved_first) == 5

    # Marcar 2 cards como "exitosas" (DDG) en el index, manualmente, simulando
    # que algunas no eran placeholder.
    import json as _json

    index_path = out / "_index.json"
    data = _json.loads(index_path.read_text(encoding="utf-8"))
    data["ARG-1"]["source"] = SOURCE_DUCKDUCKGO
    data["BRA-1"]["source"] = SOURCE_DUCKDUCKGO
    index_path.write_text(_json.dumps(data), encoding="utf-8")

    # Reinstanciar pipeline (lee el index modificado) con composer fresh
    saved_regen: list[Path] = []
    pipe2 = _make_pipeline(db_path, cid, out, saved_regen, SOURCE_DUCKDUCKGO)
    result = pipe2.regenerate_placeholders()

    # Solo las 3 que seguían como placeholder se reprocesan
    assert result.total == 3
    saved_keys = sorted(p.stem for p in saved_regen)
    assert saved_keys == ["ARG-2", "ARG-3", "BRA-2"]


def test_regenerate_placeholders_when_none(setup_collection, tmp_path):
    """Sin placeholders, regenerate_placeholders no hace nada."""
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, tmp_path / "out", photo_source=SOURCE_DUCKDUCKGO)
    pipe.run_batch()  # todos exitosos como DDG
    result = pipe.regenerate_placeholders()
    assert result.total == 0


def test_index_persists_between_runs(setup_collection, tmp_path):
    """El index sobrevive entre instancias del pipeline."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    pipe = _make_pipeline(db_path, cid, out, photo_source=SOURCE_WIKIPEDIA)
    pipe.run_batch()
    # Reinstanciar y verificar que el index ya está cargado
    pipe2 = _make_pipeline(db_path, cid, out, photo_source=SOURCE_DUCKDUCKGO)
    assert len(pipe2._index) == 5
    for entry in pipe2._index.values():
        assert entry["source"] == SOURCE_WIKIPEDIA


# ----------------------------------------------------------------------
# run_google_fill (cuota diaria) y run_resketch
# ----------------------------------------------------------------------


def _seed_placeholders(setup_collection, out_dir: Path, n: int = 5) -> ImagePipeline:
    """Genera `n` cards como placeholder vía run_batch y devuelve el pipeline."""
    db_path, cid = setup_collection
    pipe = _make_pipeline(db_path, cid, out_dir, photo_source=SOURCE_PLACEHOLDER)
    pipe.run_batch()
    assert len(pipe.get_placeholder_card_keys()) == n
    return pipe


def _fake_finder_with_google(
    cache_dir: Path,
    google_urls_per_call: list[str] | None = None,
) -> MagicMock:
    """Finder configurado para test de run_google_fill.

    `search_google_only` retorna una URL ficticia. `_download_image` crea
    un JPG válido en `dest`. `_image_has_face` retorna True. El test
    chequea cuántas veces se llamó a `search_google_only`.
    """
    finder = MagicMock()
    finder.cache_dir = cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    urls = google_urls_per_call or ["https://google.example/photo.jpg"]

    def fake_search(player_name: str, country_name: str) -> list[str]:
        del player_name, country_name
        return list(urls)

    def fake_download(url: str, dest: Path) -> bool:
        del url
        # Crear JPEG válido mínimo
        arr = np.full((200, 200, 3), 200, dtype=np.uint8)
        from PIL import Image as _Img

        _Img.fromarray(arr).save(dest, format="JPEG")
        return True

    finder.search_google_only.side_effect = fake_search
    finder._download_image.side_effect = fake_download
    finder._image_has_face.return_value = True
    return finder


def test_google_limit_respected_in_run_google_fill(setup_collection, tmp_path):
    """El daily_limit corta el procesamiento aunque haya más placeholders."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    _seed_placeholders(setup_collection, out, n=5)

    finder = _fake_finder_with_google(cache)
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
    assert finder.search_google_only.call_count == 2
    assert result.google_quota_exhausted is True
    # Y se contabilizaron como Google
    assert result.from_google == 2


def test_google_not_called_beyond_daily_limit(setup_collection, tmp_path):
    """Si daily_limit > placeholders, solo se llama lo necesario."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    _seed_placeholders(setup_collection, out, n=5)

    finder = _fake_finder_with_google(cache)
    pipe = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    result = pipe.run_google_fill(daily_limit=99)

    # Solo 5 placeholders → 5 calls, sin agotar cuota
    assert result.google_calls_used == 5
    assert finder.search_google_only.call_count == 5
    assert result.google_quota_exhausted is False
    assert result.from_google == 5


def test_google_fill_skips_when_no_placeholders(setup_collection, tmp_path):
    """Si no hay placeholders, run_google_fill retorna sin llamar a Google."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    pipe = _make_pipeline(db_path, cid, out, photo_source=SOURCE_DUCKDUCKGO)
    pipe.run_batch()

    finder = _fake_finder_with_google(cache)
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
    finder.search_google_only.assert_not_called()


def test_google_fill_updates_index_to_google_source(setup_collection, tmp_path):
    """Las cards rellenadas vía Google quedan con source=google en _index.json."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    _seed_placeholders(setup_collection, out, n=5)

    finder = _fake_finder_with_google(cache)
    pipe = ImagePipeline(
        db_path=db_path,
        collection_id=cid,
        photo_finder=finder,
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    pipe.run_google_fill(daily_limit=99)

    # Reinstanciar para forzar recarga del index desde disco
    pipe2 = _make_pipeline(db_path, cid, out, photo_source=SOURCE_PLACEHOLDER)
    google_keys = [k for k, v in pipe2._index.items() if v.get("source") == SOURCE_GOOGLE]
    assert len(google_keys) == 5


def test_run_resketch_skips_placeholders(setup_collection, tmp_path):
    """run_resketch ignora cards con source=placeholder."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    cache.mkdir(parents=True, exist_ok=True)

    # Mix de sources: 2 DDG + 3 placeholder
    pipe = _make_pipeline(db_path, cid, out, photo_source=SOURCE_PLACEHOLDER)
    pipe.run_batch()
    import json as _json

    index_path = out / "_index.json"
    data = _json.loads(index_path.read_text(encoding="utf-8"))
    data["ARG-1"]["source"] = SOURCE_DUCKDUCKGO
    data["BRA-2"]["source"] = SOURCE_DUCKDUCKGO
    index_path.write_text(_json.dumps(data), encoding="utf-8")

    # Crear los archivos cacheados de las cards no-placeholder
    for key in ("ARG-1", "BRA-2"):
        arr = np.full((200, 200, 3), 200, dtype=np.uint8)
        cv2.imwrite(str(cache / f"{key}.jpg"), arr)

    # Pipeline con finder.cache_dir apuntando al fake cache
    finder = MagicMock()
    finder.cache_dir = cache
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

    # Solo las 2 cards no-placeholder se procesan
    assert result.total == 2
    assert sketch_gen.generate_sketch.call_count == 2
    saved_keys = sorted(p.stem for p in saved)
    assert saved_keys == ["ARG-1", "BRA-2"]


def test_run_resketch_uses_cached_photos(setup_collection, tmp_path):
    """run_resketch lee las fotos desde photo_cache (no llama a find_photo)."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    cache.mkdir(parents=True, exist_ok=True)

    # Todas las cards como DDG (con foto cacheada)
    pipe = _make_pipeline(db_path, cid, out, photo_source=SOURCE_DUCKDUCKGO)
    pipe.run_batch()

    # Crear archivos de cache para todas
    for key in ("ARG-1", "ARG-2", "ARG-3", "BRA-1", "BRA-2"):
        arr = np.full((200, 200, 3), 200, dtype=np.uint8)
        cv2.imwrite(str(cache / f"{key}.jpg"), arr)

    finder = MagicMock()
    finder.cache_dir = cache
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
    """run_resketch nunca invoca find_photo ni search_google_only."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    cache.mkdir(parents=True, exist_ok=True)

    pipe = _make_pipeline(db_path, cid, out, photo_source=SOURCE_DUCKDUCKGO)
    pipe.run_batch()

    for key in ("ARG-1", "ARG-2", "ARG-3", "BRA-1", "BRA-2"):
        arr = np.full((200, 200, 3), 200, dtype=np.uint8)
        cv2.imwrite(str(cache / f"{key}.jpg"), arr)

    finder = MagicMock()
    finder.cache_dir = cache
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
    finder.search_google_only.assert_not_called()


def test_run_resketch_handles_missing_cached_photo(setup_collection, tmp_path):
    """Si el cache jpg no existe, la card se cuenta como fallida pero no rompe."""
    db_path, cid = setup_collection
    out = tmp_path / "out"
    cache = tmp_path / "photo_cache"
    cache.mkdir(parents=True, exist_ok=True)

    pipe = _make_pipeline(db_path, cid, out, photo_source=SOURCE_DUCKDUCKGO)
    pipe.run_batch()

    # No creamos ningún archivo en cache → todas deben fallar suavemente
    finder = MagicMock()
    finder.cache_dir = cache
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
