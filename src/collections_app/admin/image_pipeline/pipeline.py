"""Orquestador del pipeline de generación de imágenes.

Para cada card de la colección: PhotoFinder → SketchGenerator → CardComposer
→ guardar PNG. El procesamiento se hace en batches con callback de progreso.
Las dependencias (finder/sketch/composer) se inyectan en el constructor para
que los tests puedan mockearlas.
"""

import logging
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from threading import Event
from typing import TypedDict

from collections_app.admin.image_pipeline.card_composer import CardComposer
from collections_app.admin.image_pipeline.photo_finder import (
    SOURCE_CACHE,
    SOURCE_DUCKDUCKGO,
    SOURCE_PLACEHOLDER,
    SOURCE_WIKIPEDIA,
    PhotoFinder,
)
from collections_app.admin.image_pipeline.sketch_generator import SketchGenerator
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    CollectionsRepository,
    InventoryRepository,
)
from collections_app.core.utils.paths import (
    get_generated_cards_dir,
    get_photo_cache_dir,
)

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 100

ProgressCallback = Callable[[int, int, str], None]
LogCallback = Callable[[str, str, str], None]  # card_key, source, status


class _CardJob(TypedDict):
    """Datos compactos por card que el pipeline necesita procesar."""

    code_id: str
    card_number: int
    card_name: str
    card_key: str
    code_name: str
    owned: bool


@dataclass
class PipelineResult:
    """Resumen del run del pipeline."""

    total: int = 0
    succeeded: int = 0
    failed: int = 0
    from_cache: int = 0
    from_duckduckgo: int = 0
    from_wikipedia: int = 0
    from_placeholder: int = 0
    errors: list[str] = field(default_factory=list)
    output_dir: Path | None = None


class ImagePipeline:
    """Genera imágenes de cards en batch para una colección."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection_id: int,
        photo_finder: PhotoFinder | None = None,
        sketch_generator: SketchGenerator | None = None,
        card_composer: CardComposer | None = None,
        output_dir: Path | None = None,
    ) -> None:
        self.conn = conn
        self.collection_id = collection_id
        self._photo_finder = photo_finder or PhotoFinder(get_photo_cache_dir())
        self._sketch_generator = sketch_generator or SketchGenerator()
        self._composer = card_composer or CardComposer()
        self._output_dir = output_dir or get_generated_cards_dir(collection_id)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._stop_event = Event()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def run_batch(
        self,
        card_keys: list[str] | None = None,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        force: bool = False,
    ) -> PipelineResult:
        """Procesa cards generando sus imágenes.

        Args:
            card_keys: lista de "CODE-NUMBER" a procesar. None = todas.
            on_progress: callback `(current, total, label)` para barra de progreso.
            on_log: callback `(card_key, source, status)` para logging visual.
            batch_size: cantidad por batch (default 100). El stop signal se
                chequea entre batches.
            force: si False, omite cards que ya tienen imagen generada.

        Returns:
            `PipelineResult` con conteos por fuente y errores.
        """
        self._stop_event.clear()
        result = PipelineResult(output_dir=self._output_dir)

        all_cards = self._load_target_cards(card_keys)
        result.total = len(all_cards)

        for batch_start in range(0, len(all_cards), batch_size):
            if self._stop_event.is_set():
                break
            batch = all_cards[batch_start : batch_start + batch_size]
            for i, card in enumerate(batch, start=batch_start + 1):
                if self._stop_event.is_set():
                    break
                self._process_card(card, force, result, on_log)
                if on_progress is not None:
                    label = f"{card['card_key']} {card['card_name']}"
                    on_progress(i, result.total, label)

        return result

    def stop(self) -> None:
        """Pide al pipeline detenerse al terminar la card en curso."""
        self._stop_event.set()

    def get_output_path(self, card_key: str) -> Path:
        """Path donde está (o estará) la imagen de una card."""
        return self._output_dir / f"{card_key}.png"

    def get_existing_count(self) -> int:
        """Cuántas imágenes ya están generadas para esta colección."""
        return sum(1 for p in self._output_dir.glob("*.png"))

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_target_cards(self, card_keys: list[str] | None) -> list[_CardJob]:
        """Carga las cards de la colección (con código del header) y filtra."""
        col = CollectionsRepository(self.conn).get_by_id(self.collection_id)
        if col is None:
            raise ValueError(f"Collection {self.collection_id} no existe")

        cards = CardsRepository(self.conn).list_by_collection(self.collection_id)
        lines = {
            line.code_id: line.code_name
            for line in CodesLinesRepository(self.conn).list_by_header(col.code_header_id)
        }
        inv_owned = {
            (i.code_id, i.card_number)
            for i in InventoryRepository(self.conn).list_owned(self.collection_id)
        }

        if card_keys is not None:
            wanted = set(card_keys)
            cards = [c for c in cards if c.card_key in wanted]

        return [
            _CardJob(
                code_id=c.code_id,
                card_number=c.card_number,
                card_name=c.card_name,
                card_key=c.card_key,
                code_name=lines.get(c.code_id, c.code_id),
                owned=(c.code_id, c.card_number) in inv_owned,
            )
            for c in cards
        ]

    def _process_card(
        self,
        card: _CardJob,
        force: bool,
        result: PipelineResult,
        on_log: LogCallback | None,
    ) -> None:
        card_key = card["card_key"]
        out_path = self.get_output_path(card_key)
        if out_path.exists() and not force:
            result.from_cache += 1
            result.succeeded += 1
            if on_log is not None:
                on_log(card_key, "skip", "ok")
            return

        try:
            photo = self._photo_finder.find_photo(
                player_name=card["card_name"],
                country_name=card["code_name"],
                card_key=card_key,
            )
            sketch = self._sketch_generator.generate_sketch(photo.local_path)
            image = self._composer.compose(
                sketch=sketch,
                card_number=card["card_number"],
                player_name=card["card_name"],
                code_name=card["code_name"],
                owned=card["owned"],
            )
            self._composer.save(image, out_path)
            self._count_source(photo.source, result)
            result.succeeded += 1
            if on_log is not None:
                on_log(card_key, photo.source, "ok")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error procesando %s", card_key)
            result.failed += 1
            result.errors.append(f"{card_key}: {exc}")
            if on_log is not None:
                on_log(card_key, "error", str(exc))

    @staticmethod
    def _count_source(source: str, result: PipelineResult) -> None:
        if source == SOURCE_CACHE:
            result.from_cache += 1
        elif source == SOURCE_DUCKDUCKGO:
            result.from_duckduckgo += 1
        elif source == SOURCE_WIKIPEDIA:
            result.from_wikipedia += 1
        elif source == SOURCE_PLACEHOLDER:
            result.from_placeholder += 1
