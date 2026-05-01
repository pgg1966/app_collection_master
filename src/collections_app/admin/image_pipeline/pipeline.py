"""Orquestador del pipeline de generación de imágenes.

Para cada card de la colección: PhotoFinder → SketchGenerator → CardComposer
→ guardar PNG. El procesamiento se hace en batches con callback de progreso.
Las dependencias (finder/sketch/composer) se inyectan en el constructor para
que los tests puedan mockearlas.

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
    MAX_URLS_PER_QUERY,
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
INDEX_FILE_NAME = "_index.json"

# Google Custom Search free tier permite 100 queries/día. Reservamos 1
# para nosotros (margen de error / debug) y dejamos 99 para el modo
# `run_google_fill`. El contador es por sesión (no persistido en disco):
# si la app se reinicia el mismo día y se vuelve a invocar
# `run_google_fill`, el contador arranca en 0 — la responsabilidad de no
# exceder la cuota real de Google queda en el operador.
GOOGLE_DAILY_LIMIT = 99

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
        # `_index.json` mapea card_key → {"source": ..., "url": ...}.
        # Persistido en el output_dir para sobrevivir entre runs.
        self._index_path = self._output_dir / INDEX_FILE_NAME
        self._index: dict[str, dict[str, str]] = self._load_index()

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

        Abre una conexión SQLite propia (lo que permite ejecutar el método
        dentro de un QThread) y la cierra al terminar el run.

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

        conn = self._open_connection()
        try:
            all_cards = self._load_target_cards(conn, card_keys)
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
                # Persistir el index al cerrar cada batch para sobrevivir a stops
                self._save_index()
        finally:
            self._save_index()
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

        Útil para `regenerate_placeholders()`. Si el index no existe aún
        (corrida vieja sin _index.json), devuelve lista vacía.
        """
        return sorted(
            key for key, info in self._index.items() if info.get("source") == SOURCE_PLACEHOLDER
        )

    def regenerate_placeholders(
        self,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
    ) -> PipelineResult:
        """Borra los PNGs de cards que cayeron a placeholder y los reprocesa.

        El reprocesamiento usa la lógica normal del pipeline (incluyendo
        las queries mejoradas y la validación por face detection), por lo
        que un jugador que la primera vez fue placeholder puede ahora
        encontrar foto real.

        También limpia las fotos crudas del caché de esos cards (si no,
        el pipeline volvería a leer la imagen vieja desde caché).
        """
        keys = self.get_placeholder_card_keys()
        if not keys:
            return PipelineResult(output_dir=self._output_dir)

        # Borrar PNGs y fotos crudas para forzar re-búsqueda
        for key in keys:
            png = self.get_output_path(key)
            png.unlink(missing_ok=True)
            cached_photo = self._photo_finder.cache_dir / f"{key}.jpg"
            cached_photo.unlink(missing_ok=True)
            self._index.pop(key, None)
        self._save_index()

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
        """Procesa SOLO las cards que actualmente son placeholder usando Google.

        Por cada placeholder, gasta 1 query a Google Custom Search. Se
        detiene apenas se alcanza `daily_limit` (default 99 — la API
        free permite 100/día y reservamos 1 de margen). Si el download
        o la validación fallan, igual se cuenta el call (porque la API
        ya nos cobró la query) y se deja el placeholder como estaba.

        Si Google no está configurado (`GOOGLE_API_KEY`/`GOOGLE_CSE_ID`
        no presentes en env), retorna inmediatamente sin tocar nada.
        """
        self._stop_event.clear()
        result = PipelineResult(output_dir=self._output_dir)
        keys = self.get_placeholder_card_keys()
        if not keys:
            return result

        conn = self._open_connection()
        try:
            jobs = self._load_target_cards(conn, keys)
            jobs_by_key = {j["card_key"]: j for j in jobs}
            result.total = len(keys)
            calls_used = 0

            for i, key in enumerate(keys, start=1):
                if self._stop_event.is_set():
                    break
                if calls_used >= daily_limit:
                    result.google_quota_exhausted = True
                    break
                job = jobs_by_key.get(key)
                if job is None:
                    continue
                calls_used += 1
                self._google_fill_one(job, result, on_log)
                if on_progress is not None:
                    label = f"{key} {job['card_name']} (Google {calls_used}/{daily_limit})"
                    on_progress(i, result.total, label)
            self._save_index()
        finally:
            self._save_index()
            conn.close()

        result.google_calls_used = calls_used
        return result

    def run_resketch(
        self,
        on_progress: ProgressCallback | None = None,
        on_log: LogCallback | None = None,
    ) -> PipelineResult:
        """Re-aplica el algoritmo de sketch a las fotos cacheadas.

        Útil tras cambiar el algoritmo de sketch (p.ej. Nivel 3 → Nivel 4):
        regenera el PNG final usando la foto cruda en `photo_cache/` sin
        salir a internet. Se saltan los placeholders (su sketch se
        regenera con `regenerate_placeholders` o `run_google_fill`).
        """
        self._stop_event.clear()
        result = PipelineResult(output_dir=self._output_dir)

        # Cards con foto real cacheada (cualquier source que no sea placeholder).
        target_keys = sorted(
            key
            for key, info in self._index.items()
            if info.get("source") and info["source"] != SOURCE_PLACEHOLDER
        )
        if not target_keys:
            return result

        conn = self._open_connection()
        try:
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
        return conn

    def _load_index(self) -> dict[str, dict[str, str]]:
        """Carga el `_index.json` del output_dir o retorna dict vacío."""
        if not self._index_path.exists():
            return {}
        try:
            with self._index_path.open(encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return data
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("No se pudo leer %s: %s", self._index_path, exc)
        return {}

    def _save_index(self) -> None:
        """Guarda el `_index.json` con las entradas actuales."""
        try:
            with self._index_path.open("w", encoding="utf-8") as fh:
                json.dump(self._index, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            logger.warning("No se pudo escribir %s: %s", self._index_path, exc)

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
            self._index[card_key] = {
                "source": photo.source,
                "url": photo.source_url,
            }
            if on_log is not None:
                on_log(card_key, photo.source, "ok")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error procesando %s", card_key)
            result.failed += 1
            result.errors.append(f"{card_key}: {exc}")
            if on_log is not None:
                on_log(card_key, "error", str(exc))

    def _google_fill_one(
        self,
        card: _CardJob,
        result: PipelineResult,
        on_log: LogCallback | None,
    ) -> None:
        """Procesa una card vía Google. Cada llamada gasta 1 query."""
        card_key = card["card_key"]
        cached_jpg = self._photo_finder.cache_dir / f"{card_key}.jpg"
        urls = self._photo_finder.search_google_only(
            player_name=card["card_name"], country_name=card["code_name"]
        )

        # Si Google no devolvió nada (no configurado o sin resultados),
        # mantenemos el placeholder y reportamos error suave.
        if not urls:
            result.failed += 1
            if on_log is not None:
                on_log(card_key, SOURCE_GOOGLE, "no_results")
            return

        # Probamos hasta MAX_URLS_PER_QUERY URLs candidatas.
        for url in urls[:MAX_URLS_PER_QUERY]:
            # Borrar el placeholder cacheado antes de intentar el download
            # nuevo (si no, _download_image podría no sobreescribirlo).
            cached_jpg.unlink(missing_ok=True)
            if not self._photo_finder._download_image(url, cached_jpg):
                continue
            if not self._photo_finder._image_has_face(cached_jpg):
                cached_jpg.unlink(missing_ok=True)
                continue
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
            except Exception as exc:  # noqa: BLE001
                logger.exception("Google fill: error procesando %s", card_key)
                result.failed += 1
                result.errors.append(f"{card_key}: {exc}")
                if on_log is not None:
                    on_log(card_key, SOURCE_GOOGLE, str(exc))
                return
            result.from_google += 1
            result.succeeded += 1
            self._index[card_key] = {"source": SOURCE_GOOGLE, "url": url}
            if on_log is not None:
                on_log(card_key, SOURCE_GOOGLE, "ok")
            return

        # Todas las URLs candidatas fallaron download/validación.
        result.failed += 1
        if on_log is not None:
            on_log(card_key, SOURCE_GOOGLE, "all_urls_invalid")

    def _resketch_one(
        self,
        card: _CardJob,
        result: PipelineResult,
        on_log: LogCallback | None,
    ) -> None:
        """Re-aplica sketch+compose a una card que ya tiene foto cacheada."""
        card_key = card["card_key"]
        cached_jpg = self._photo_finder.cache_dir / f"{card_key}.jpg"
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
