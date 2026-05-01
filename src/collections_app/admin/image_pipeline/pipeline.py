"""Orquestador del pipeline de generación de imágenes.

Para cada card de la colección: PhotoFinder → SketchGenerator → CardComposer
→ guardar PNG. El procesamiento se hace en batches con callback de progreso.
Las dependencias (finder/sketch/composer) se inyectan en el constructor para
que los tests puedan mockearlas.

Tracking persistido en la tabla `card_images` (migración 003): cada card
queda con `found_photo` (1=foto real, 0=placeholder) + `image_source` +
`image_path`. Reemplaza al `_index.json` que usábamos antes; si todavía
hay un JSON viejo en el output_dir lo ingestamos automáticamente y lo
renombramos a `.legacy`.

Threading note: el pipeline normalmente corre dentro de un QThread (ver
`PipelineWorker`). SQLite no permite compartir conexiones entre threads,
así que el pipeline NO recibe una conexión: recibe un `db_path` y abre
una conexión propia dentro de `run_batch()` (ya en el worker thread). La
cierra al finalizar el run.
"""

import json
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
    SOURCE_GOOGLE,
    SOURCE_PLACEHOLDER,
    SOURCE_WIKIPEDIA,
    PhotoFinder,
)
from collections_app.admin.image_pipeline.sketch_generator import SketchGenerator
from collections_app.core.db.connection import create_connection
from collections_app.core.db.migrator import run_migrations
from collections_app.core.models import CardImage
from collections_app.core.repositories import (
    CardImagesRepository,
    CardsRepository,
    CodesLinesRepository,
    CollectionsRepository,
    InventoryRepository,
)
from collections_app.core.utils.datetime_helpers import format_for_db, utc_now
from collections_app.core.utils.paths import (
    get_generated_cards_dir,
    get_photo_cache_dir,
)

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 100
LEGACY_INDEX_FILENAME = "_index.json"  # ingestado y renombrado a .legacy

# Google Custom Search free tier permite 100 queries/día. El contador
# es por sesión (no persistido en disco): si la app se reinicia el mismo
# día y se vuelve a invocar `run_google_fill`, el contador arranca en 0
# — la responsabilidad de no exceder la cuota real de Google queda en
# el operador.
GOOGLE_DAILY_LIMIT = 100

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
    from_google: int = 0
    from_placeholder: int = 0
    google_calls_used: int = 0
    google_quota_exhausted: bool = False
    errors: list[str] = field(default_factory=list)
    output_dir: Path | None = None


class ImagePipeline:
    """Genera imágenes de cards en batch para una colección.

    El constructor recibe un `db_path` (no una conexión): la conexión se
    abre dentro de `run_batch()`, ya en el thread donde corre, y se cierra
    al terminar. Esto evita el `sqlite3.ProgrammingError: SQLite objects
    created in a thread can only be used in that same thread`.
    """

    def __init__(
        self,
        db_path: Path,
        collection_id: int,
        photo_finder: PhotoFinder | None = None,
        sketch_generator: SketchGenerator | None = None,
        card_composer: CardComposer | None = None,
        output_dir: Path | None = None,
    ) -> None:
        self._db_path = db_path
        self.collection_id = collection_id
        self._photo_finder = photo_finder or PhotoFinder(get_photo_cache_dir())
        self._sketch_generator = sketch_generator or SketchGenerator()
        self._composer = card_composer or CardComposer()
        self._output_dir = output_dir or get_generated_cards_dir(collection_id)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._stop_event = Event()
        self._legacy_index_path = self._output_dir / LEGACY_INDEX_FILENAME

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
        """Procesa cards generando sus imágenes."""
        self._stop_event.clear()
        result = PipelineResult(output_dir=self._output_dir)

        conn = self._open_connection()
        try:
            repo = CardImagesRepository(conn)
            all_cards = self._load_target_cards(conn, card_keys)
            result.total = len(all_cards)

            for batch_start in range(0, len(all_cards), batch_size):
                if self._stop_event.is_set():
                    break
                batch = all_cards[batch_start : batch_start + batch_size]
                for i, card in enumerate(batch, start=batch_start + 1):
                    if self._stop_event.is_set():
                        break
                    self._process_card(card, force, result, repo, on_log)
                    if on_progress is not None:
                        label = f"{card['card_key']} {card['card_name']}"
                        on_progress(i, result.total, label)
                conn.commit()
        finally:
            conn.commit()
            conn.close()

        return result

    def stop(self) -> None:
        """Pide al pipeline detenerse al terminar la card en curso."""
        self._stop_event.set()

    def get_output_path(self, card_key: str) -> Path:
        """Path donde está (o estará) la imagen de una card."""
        return self._output_dir / f"{card_key}.png"

    def get_existing_count(self) -> int:
        """Cuántas imágenes ya están generadas para esta colección.

        No requiere DB; lee el filesystem (solo cuenta `*.png`).
        """
        return sum(1 for p in self._output_dir.glob("*.png"))

    def get_placeholder_card_keys(self) -> list[str]:
        """Card keys cuya imagen actual fue generada vía placeholder.

        Lee de `card_images` (found_photo=0). Si la pipeline nunca corrió
        en esta colección la lista queda vacía.
        """
        conn = self._open_connection()
        try:
            placeholders = CardImagesRepository(conn).get_placeholders(self.collection_id)
            return sorted(f"{p.code_id}-{p.card_number}" for p in placeholders)
        finally:
            conn.close()

    def get_found_count(self) -> int:
        """Cuántas cards tienen `found_photo=True` en card_images."""
        conn = self._open_connection()
        try:
            return CardImagesRepository(conn).get_found_count(self.collection_id)
        finally:
            conn.close()

    def get_total_generated(self) -> int:
        """Cuántas cards tienen alguna imagen registrada (real o placeholder)."""
        conn = self._open_connection()
        try:
            return CardImagesRepository(conn).get_total_generated(self.collection_id)
        finally:
            conn.close()

    def regenerate_placeholders(
        self,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
    ) -> PipelineResult:
        """Borra los PNGs de cards que cayeron a placeholder y los reprocesa."""
        keys = self.get_placeholder_card_keys()
        if not keys:
            return PipelineResult(output_dir=self._output_dir)

        # Borrar PNGs viejos para forzar reprocesamiento.
        # Las fotos crudas en cache_dir son por jugador (compartidas), así
        # que NO las borramos: si otra colección las descargó, valen.
        for key in keys:
            self.get_output_path(key).unlink(missing_ok=True)

        return self.run_batch(
            card_keys=keys,
            on_progress=on_progress,
            on_log=on_log,
            force=True,
        )

    def run_google_fill(
        self,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
        daily_limit: int = GOOGLE_DAILY_LIMIT,
    ) -> PipelineResult:
        """Reintenta la cascada completa para las cards en placeholder.

        Procesa SOLO cards con `found_photo=0` en `card_images`. Para
        cada una intenta la cascada Wikipedia → DuckDuckGo → Google CSE.
        Las queries a Google se cuentan en `photo_finder.google_calls_used`
        y la cascada deja de probar Google al llegar a `daily_limit`.

        Las cards que sigan fallando quedan como placeholder y se pueden
        reintentar mañana (cuando la cuota de Google se renueva).
        """
        self._stop_event.clear()
        result = PipelineResult(output_dir=self._output_dir)
        keys = self.get_placeholder_card_keys()
        if not keys:
            return result

        # Resetear contador y fijar la cuota en el finder.
        self._photo_finder.google_calls_used = 0
        self._photo_finder.google_quota = daily_limit

        conn = self._open_connection()
        try:
            repo = CardImagesRepository(conn)
            jobs = self._load_target_cards(conn, keys)
            result.total = len(jobs)
            for i, job in enumerate(jobs, start=1):
                if self._stop_event.is_set():
                    break
                # Borrar el PNG viejo para forzar regeneración.
                self.get_output_path(job["card_key"]).unlink(missing_ok=True)
                # Borrar el cache del jugador para que no use el placeholder
                # cacheado de un run previo (el placeholder NO se cachea
                # como foto del jugador, pero por las dudas).
                cached = self._photo_finder.cached_photo_path(job["card_name"], job["code_id"])
                cached.unlink(missing_ok=True)

                self._process_card(job, force=True, result=result, repo=repo, on_log=on_log)

                if on_progress is not None:
                    used = self._photo_finder.google_calls_used
                    label = (
                        f"{job['card_key']} {job['card_name']} " f"(Google {used}/{daily_limit})"
                    )
                    on_progress(i, result.total, label)
            conn.commit()
        finally:
            conn.commit()
            conn.close()

        result.google_calls_used = self._photo_finder.google_calls_used
        result.google_quota_exhausted = result.google_calls_used >= daily_limit
        return result

    def run_resketch(
        self,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
    ) -> PipelineResult:
        """Re-aplica el algoritmo de sketch a las fotos cacheadas.

        Útil tras cambiar el algoritmo de sketch: regenera el PNG final
        usando la foto cruda en `photo_cache/` sin salir a internet. Se
        saltan los placeholders (su sketch se regenera con
        `regenerate_placeholders` o `run_google_fill`).
        """
        self._stop_event.clear()
        result = PipelineResult(output_dir=self._output_dir)

        conn = self._open_connection()
        try:
            images = CardImagesRepository(conn).list_by_collection(self.collection_id)
            target_keys = sorted(
                f"{img.code_id}-{img.card_number}" for img in images if img.found_photo
            )
            if not target_keys:
                return result

            jobs = self._load_target_cards(conn, target_keys)
            result.total = len(jobs)
            for i, job in enumerate(jobs, start=1):
                if self._stop_event.is_set():
                    break
                self._resketch_one(job, result, on_log)
                if on_progress is not None:
                    on_progress(i, result.total, f"{job['card_key']} {job['card_name']}")
        finally:
            conn.close()

        return result

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _open_connection(self) -> sqlite3.Connection:
        """Abre y retorna una nueva conexión a la DB. Migra por las dudas."""
        conn = create_connection(self._db_path)
        run_migrations(conn)
        # Ingesto del _index.json viejo si existe (one-shot)
        self._ingest_legacy_index_if_needed(conn)
        return conn

    def _ingest_legacy_index_if_needed(self, conn: sqlite3.Connection) -> None:
        """Migra entries de `_index.json` (antes de migración 003) a card_images.

        Sólo corre una vez: tras importar, renombra el archivo a `.legacy`.
        Si ya hay datos en `card_images` para esta colección no pisa nada.
        """
        if not self._legacy_index_path.exists():
            return
        repo = CardImagesRepository(conn)
        if repo.get_total_generated(self.collection_id) > 0:
            # Ya hay datos en card_images para esta colección, no pisar.
            return
        try:
            with self._legacy_index_path.open(encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("No se pudo leer legacy index %s: %s", self._legacy_index_path, exc)
            return
        if not isinstance(data, dict):
            return

        now = format_for_db(utc_now())
        ingested = 0
        for card_key, info in data.items():
            if not isinstance(info, dict):
                continue
            source = info.get("source")
            if not source:
                continue
            try:
                code_id, num_str = card_key.rsplit("-", 1)
                num = int(num_str)
            except (ValueError, AttributeError):
                continue
            repo.upsert(
                CardImage(
                    collection_id=self.collection_id,
                    code_id=code_id,
                    card_number=num,
                    found_photo=(source != SOURCE_PLACEHOLDER),
                    image_source=source,
                    image_path=str(self.get_output_path(card_key)),
                    generated_at=now,
                )
            )
            ingested += 1
        conn.commit()
        logger.info("Ingestadas %d entries de %s", ingested, self._legacy_index_path)
        # Renombrar a .legacy para no volver a procesar
        self._legacy_index_path.rename(self._legacy_index_path.with_suffix(".json.legacy"))

    def _load_target_cards(
        self,
        conn: sqlite3.Connection,
        card_keys: list[str] | None,
    ) -> list[_CardJob]:
        """Carga las cards de la colección (con código del header) y filtra."""
        col = CollectionsRepository(conn).get_by_id(self.collection_id)
        if col is None:
            raise ValueError(f"Collection {self.collection_id} no existe")

        cards = CardsRepository(conn).list_by_collection(self.collection_id)
        lines = {
            line.code_id: line.code_name
            for line in CodesLinesRepository(conn).list_by_header(col.code_header_id)
        }
        inv_owned = {
            (i.code_id, i.card_number)
            for i in InventoryRepository(conn).list_owned(self.collection_id)
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
        repo: CardImagesRepository,
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
                country_code=card["code_id"],
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
            repo.upsert(
                CardImage(
                    collection_id=self.collection_id,
                    code_id=card["code_id"],
                    card_number=card["card_number"],
                    found_photo=(photo.source != SOURCE_PLACEHOLDER),
                    image_source=photo.source,
                    image_path=str(out_path),
                    generated_at=format_for_db(utc_now()),
                )
            )
            if on_log is not None:
                on_log(card_key, photo.source, "ok")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error procesando %s", card_key)
            result.failed += 1
            result.errors.append(f"{card_key}: {exc}")
            if on_log is not None:
                on_log(card_key, "error", str(exc))

    def _resketch_one(
        self,
        card: _CardJob,
        result: PipelineResult,
        on_log: LogCallback | None,
    ) -> None:
        """Re-aplica sketch+compose a una card que ya tiene foto cacheada."""
        card_key = card["card_key"]
        cached_jpg = self._photo_finder.cached_photo_path(card["card_name"], card["code_id"])
        if not cached_jpg.exists():
            # El index dice que tiene foto pero el archivo no está; saltar.
            result.failed += 1
            if on_log is not None:
                on_log(card_key, "resketch", "no_cached_photo")
            return
        try:
            sketch = self._sketch_generator.generate_sketch(cached_jpg)
            image = self._composer.compose(
                sketch=sketch,
                card_number=card["card_number"],
                player_name=card["card_name"],
                code_name=card["code_name"],
                owned=card["owned"],
            )
            self._composer.save(image, self.get_output_path(card_key))
            result.succeeded += 1
            if on_log is not None:
                on_log(card_key, "resketch", "ok")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Resketch: error procesando %s", card_key)
            result.failed += 1
            result.errors.append(f"{card_key}: {exc}")
            if on_log is not None:
                on_log(card_key, "resketch", str(exc))

    @staticmethod
    def _count_source(source: str, result: PipelineResult) -> None:
        if source == SOURCE_CACHE:
            result.from_cache += 1
        elif source == SOURCE_DUCKDUCKGO:
            result.from_duckduckgo += 1
        elif source == SOURCE_WIKIPEDIA:
            result.from_wikipedia += 1
        elif source == SOURCE_GOOGLE:
            result.from_google += 1
        elif source == SOURCE_PLACEHOLDER:
            result.from_placeholder += 1
