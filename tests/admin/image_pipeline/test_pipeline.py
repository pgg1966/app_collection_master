"""Tests del ImagePipeline con dependencias mockeadas."""

from pathlib import Path
from unittest.mock import MagicMock

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
from collections_app.core.models import Card, CodeLine
from collections_app.core.repositories import CardsRepository, CodesLinesRepository


@pytest.fixture
def setup_collection(memory_db, sample_collection):
    """Crea cards (5) y code_lines en la colección."""
    hid = sample_collection.code_header_id
    cid = sample_collection.collection_id
    lines = CodesLinesRepository(memory_db)
    for code, name in [("ARG", "ARGENTINA"), ("BRA", "BRAZIL")]:
        lines.upsert(CodeLine(hid, code, name))

    cards = CardsRepository(memory_db)
    cards.upsert(Card(cid, "ARG", 1, "Messi"))
    cards.upsert(Card(cid, "ARG", 2, "Martinez"))
    cards.upsert(Card(cid, "ARG", 3, "Molina"))
    cards.upsert(Card(cid, "BRA", 1, "Vinicius"))
    cards.upsert(Card(cid, "BRA", 2, "Neymar"))
    memory_db.commit()
    return sample_collection


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
    """Mock que retorna un sketch numpy uniforme."""
    gen = MagicMock()
    gen.generate_sketch.return_value = np.full((310, 260), 200, dtype=np.uint8)
    return gen


def _fake_composer(saved_paths: list[Path]) -> MagicMock:
    """Mock del composer: registra los paths donde se "guardaron" cards."""
    composer = MagicMock()
    composer.compose.return_value = Image.new("RGB", (280, 380), (200, 200, 200))

    def save(_image, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.touch()
        saved_paths.append(output_path)

    composer.save.side_effect = save
    return composer


def _make_pipeline(
    memory_db,
    collection,
    tmp_path: Path,
    saved_paths: list[Path] | None = None,
    photo_source: str = SOURCE_DUCKDUCKGO,
) -> ImagePipeline:
    saved_paths = saved_paths if saved_paths is not None else []
    return ImagePipeline(
        conn=memory_db,
        collection_id=collection.collection_id,
        photo_finder=_fake_photo_finder(photo_source),
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer(saved_paths),
        output_dir=tmp_path / "out",
    )


def test_skips_already_generated_cards(memory_db, setup_collection, tmp_path):
    """Cards con PNG existente se cuentan como cache, no se reprocesan."""
    saved: list[Path] = []
    pipe = _make_pipeline(memory_db, setup_collection, tmp_path, saved)
    # Crear PNG previo para una de las cards
    (tmp_path / "out").mkdir(exist_ok=True)
    (tmp_path / "out" / "ARG-1.png").touch()

    result = pipe.run_batch()
    assert result.total == 5
    assert result.succeeded == 5
    assert result.from_cache >= 1
    # ARG-1 NO debió pasar por el composer
    saved_keys = [p.stem for p in saved]
    assert "ARG-1" not in saved_keys


def test_processes_in_batches(memory_db, setup_collection, tmp_path):
    saved: list[Path] = []
    pipe = _make_pipeline(memory_db, setup_collection, tmp_path, saved)
    progress: list[tuple[int, int, str]] = []
    result = pipe.run_batch(
        on_progress=lambda c, t, n: progress.append((c, t, n)),
        batch_size=2,
    )
    assert result.total == 5
    # Último callback con i=5
    assert progress[-1][0] == 5
    assert progress[-1][1] == 5


def test_progress_callback_called_per_card(memory_db, setup_collection, tmp_path):
    pipe = _make_pipeline(memory_db, setup_collection, tmp_path)
    calls = 0

    def cb(_c: int, _t: int, _n: str) -> None:
        nonlocal calls
        calls += 1

    pipe.run_batch(on_progress=cb)
    assert calls == 5


def test_result_counts_sources_correctly(memory_db, setup_collection, tmp_path):
    pipe = _make_pipeline(memory_db, setup_collection, tmp_path, photo_source=SOURCE_WIKIPEDIA)
    result = pipe.run_batch()
    assert result.from_wikipedia == 5


def test_stop_signal_halts_after_batch(memory_db, setup_collection, tmp_path):
    """Llamar stop() durante la ejecución corta el loop entre batches."""
    saved: list[Path] = []
    pipe = _make_pipeline(memory_db, setup_collection, tmp_path, saved)

    def cb(c: int, _t: int, _n: str) -> None:
        if c == 2:
            pipe.stop()

    result = pipe.run_batch(on_progress=cb, batch_size=2)
    # Tras el primer batch (2 cards), stop activo → no procesa el resto
    assert result.succeeded <= 2


def test_force_regenerates_existing(memory_db, setup_collection, tmp_path):
    saved: list[Path] = []
    pipe = _make_pipeline(memory_db, setup_collection, tmp_path, saved)
    (tmp_path / "out").mkdir(exist_ok=True)
    (tmp_path / "out" / "ARG-1.png").write_bytes(b"old")

    pipe.run_batch(force=True)
    # ARG-1 fue procesada (re-saved)
    saved_keys = [p.stem for p in saved]
    assert "ARG-1" in saved_keys


def test_placeholder_counted_separately(memory_db, setup_collection, tmp_path):
    pipe = _make_pipeline(memory_db, setup_collection, tmp_path, photo_source=SOURCE_PLACEHOLDER)
    result = pipe.run_batch()
    assert result.from_placeholder == 5
    assert result.from_duckduckgo == 0


def test_output_dir_created_automatically(memory_db, setup_collection, tmp_path):
    out = tmp_path / "deep" / "nested" / "out"
    pipe = ImagePipeline(
        conn=memory_db,
        collection_id=setup_collection.collection_id,
        photo_finder=_fake_photo_finder(),
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=out,
    )
    pipe.run_batch()
    assert out.exists()


def test_card_keys_filter(memory_db, setup_collection, tmp_path):
    """Pasar `card_keys` restringe el procesamiento a esas cards."""
    saved: list[Path] = []
    pipe = _make_pipeline(memory_db, setup_collection, tmp_path, saved)
    result = pipe.run_batch(card_keys=["ARG-1", "BRA-2"])
    assert result.total == 2
    saved_keys = sorted(p.stem for p in saved)
    assert saved_keys == ["ARG-1", "BRA-2"]


def test_get_existing_count(memory_db, setup_collection, tmp_path):
    pipe = _make_pipeline(memory_db, setup_collection, tmp_path)
    assert pipe.get_existing_count() == 0
    pipe.run_batch()
    assert pipe.get_existing_count() == 5


def test_unknown_collection_raises(memory_db, tmp_path):
    pipe = ImagePipeline(
        conn=memory_db,
        collection_id=9999,
        photo_finder=_fake_photo_finder(),
        sketch_generator=_fake_sketch_generator(),
        card_composer=_fake_composer([]),
        output_dir=tmp_path / "out",
    )
    with pytest.raises(ValueError, match="no existe"):
        pipe.run_batch()
