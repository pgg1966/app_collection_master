"""Generador de álbum PDF imprimible (únicas + repetidas) usando escudos.

Cada slot del álbum muestra:
  - Fondo coloreado (celeste si la card está, blanco hueso si falta).
  - El ESCUDO del code_id (un PNG por código en `get_crest_path()`),
    centrado y con transparencia.
  - Línea separadora.
  - "#NUMERO  NOMBRE_JUGADOR" debajo.
  - Badge rojo con "x{N}" en el modo "duplicates".

Layout A4 vertical:
  - Margen exterior 10mm.
  - Header oscuro de 12mm con nombre del grupo + número de página.
  - Grilla 4×3 cards por defecto (configurable).
  - Footer 6mm con colección + fecha.

Cada nuevo `code_id` empieza en una página nueva.

reportlab usa puntos como unidad nativa (1pt = 1/72 inch). Las constantes
en mm se convierten via `* mm`.
"""

import logging
import sqlite3
from collections.abc import Callable
from dataclasses import dataclass, field
from itertools import groupby
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from collections_app.core.models import Card, Collection, InventoryItem
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    InventoryRepository,
)
from collections_app.core.utils.datetime_helpers import format_for_display, utc_now
from collections_app.core.utils.paths import get_crest_path

logger = logging.getLogger(__name__)

# Geometría (todo en mm; se convierte a puntos al pasarlo a reportlab)
PAGE_W_MM = 210
PAGE_H_MM = 297
MARGIN_MM = 10
GAP_MM = 4
HEADER_H_MM = 12
LABEL_H_MM = 9
FOOTER_H_MM = 6
SEPARATOR_PAD_MM = 1.5

# Card aspect ratio (Adrenalyn): 9 alto × 7 ancho.
CARD_RATIO_H_OVER_W = 9 / 7

# Fracción del slot que ocupa el escudo (alto)
CREST_SCALE = 0.55

# Colores
COLOR_HEADER_BG = HexColor("#2c3e50")
COLOR_HEADER_FG = white
COLOR_OWNED_BG = HexColor("#b8d4e8")  # celeste
COLOR_MISSING_BG = HexColor("#f5f5f0")  # blanco hueso
COLOR_BADGE = HexColor("#c8102e")
COLOR_BADGE_FG = white
COLOR_BORDER = HexColor("#404040")
COLOR_LABEL_FG = HexColor("#1f1f1f")
COLOR_FOOTER_FG = HexColor("#606060")
COLOR_SEPARATOR = HexColor("#909090")

MAX_NAME_CHARS = 22


@dataclass
class AlbumConfig:
    """Configuración del álbum a generar."""

    cols: int = 4
    rows: int = 3
    show_owned: bool = True
    show_missing: bool = True
    title: str = ""


@dataclass
class CardSlotData:
    """Datos compactos por card que se dibujan en el PDF."""

    card: Card
    inventory_item: InventoryItem | None
    code_name: str
    code_order: int
    crest_path: Path | None

    @property
    def is_owned(self) -> bool:
        return self.inventory_item is not None and self.inventory_item.quantity > 0

    @property
    def quantity(self) -> int:
        return self.inventory_item.quantity if self.inventory_item is not None else 0


@dataclass
class SlotsByGroup:
    """Slots agrupados por code_id, listos para paginar."""

    groups: list[tuple[str, str, list[CardSlotData]]] = field(default_factory=list)
    """Lista de (code_id, code_name, slots)."""


class PdfAlbumGenerator:
    """Genera PDFs imprimibles del álbum (únicas / repetidas) y listas TXT."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        collection: Collection,
        config: AlbumConfig | None = None,
    ) -> None:
        self.conn = conn
        self.collection = collection
        self.config = config or AlbumConfig()
        self._crest_cache: dict[str, ImageReader | None] = {}

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def generate_unique_album(
        self,
        output_path: Path,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> Path:
        """Genera el álbum principal (todas las cards filtradas por config)."""
        slots = self._build_slot_data()
        slots = self._filter_by_config(slots)
        groups = self._group_by_code(slots)
        self._render(output_path, groups, on_progress, mode="unique")
        return output_path

    def generate_duplicates_album(
        self,
        output_path: Path,
        on_progress: Callable[[int, int], None] | None = None,
    ) -> Path:
        """Genera el álbum de repetidas (solo qty > 1) con badge xN."""
        all_slots = self._build_slot_data()
        dup_slots = [s for s in all_slots if s.quantity > 1]
        groups = self._group_by_code(dup_slots)
        self._render(
            output_path,
            groups,
            on_progress,
            mode="duplicates",
            empty_message="No tenés repetidas en esta colección.",
        )
        return output_path

    def export_missing_list(self, output_path: Path) -> Path:
        """Exporta TXT de faltantes agrupado por código."""
        slots = self._build_slot_data()
        missing = [s for s in slots if not s.is_owned]
        lines = self._format_list_header("FALTANTES", len(missing), len(slots))
        for code_id, code_name, group_slots in self._group_by_code(missing).groups:
            lines.append("")
            lines.append(f"{code_name} ({code_id})")
            for slot in group_slots:
                name = self._truncate(slot.card.card_name, 30)
                lines.append(f"  #{slot.card.card_number:<3} {name}")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return output_path

    def export_duplicates_list(self, output_path: Path) -> Path:
        """Exporta TXT de repetidas con cantidad de copias extra."""
        slots = self._build_slot_data()
        dups = [s for s in slots if s.quantity > 1]
        total_extra = sum(s.quantity - 1 for s in dups)
        lines = self._format_list_header("REPETIDAS", total_extra, kind="copias extra")
        if not dups:
            lines.append("")
            lines.append("No tenés repetidas en esta colección.")
        else:
            for code_id, code_name, group_slots in self._group_by_code(dups).groups:
                lines.append("")
                lines.append(f"{code_name} ({code_id})")
                for slot in group_slots:
                    name = self._truncate(slot.card.card_name, 30)
                    extra = slot.quantity - 1
                    pad_dots = max(1, 35 - len(name) - 5)
                    lines.append(
                        f"  #{slot.card.card_number:<3} {name} " f"{'.' * pad_dots} ×{extra}"
                    )
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return output_path

    # ------------------------------------------------------------------
    # Carga de datos
    # ------------------------------------------------------------------

    def _build_slot_data(self) -> list[CardSlotData]:
        """Carga catálogo + inventory + lookup de escudo y code_name."""
        assert self.collection.collection_id is not None
        cid: int = self.collection.collection_id

        cards = CardsRepository(self.conn).list_by_collection(cid)
        inv = {
            (i.code_id, i.card_number): i
            for i in InventoryRepository(self.conn).list_by_collection(cid)
        }
        lines = CodesLinesRepository(self.conn).list_by_header(self.collection.code_header_id)
        code_meta = {line.code_id: (line.code_name, line.code_order) for line in lines}

        slots: list[CardSlotData] = []
        for card in cards:
            code_name, code_order = code_meta.get(card.code_id, (card.code_id, 0))
            crest_path = get_crest_path(card.code_id)
            slot = CardSlotData(
                card=card,
                inventory_item=inv.get((card.code_id, card.card_number)),
                code_name=code_name,
                code_order=code_order,
                crest_path=crest_path if crest_path.exists() else None,
            )
            slots.append(slot)
        slots.sort(key=lambda s: (s.code_order, s.card.code_id, s.card.card_number))
        return slots

    def _filter_by_config(self, slots: list[CardSlotData]) -> list[CardSlotData]:
        result = list(slots)
        if not self.config.show_missing:
            result = [s for s in result if s.is_owned]
        if not self.config.show_owned:
            result = [s for s in result if not s.is_owned]
        return result

    def _group_by_code(self, slots: list[CardSlotData]) -> SlotsByGroup:
        result = SlotsByGroup()
        ordered = sorted(slots, key=lambda s: (s.code_order, s.card.code_id))
        for code_id, group in groupby(ordered, key=lambda s: s.card.code_id):
            group_list = list(group)
            code_name = group_list[0].code_name if group_list else code_id
            result.groups.append((code_id, code_name, group_list))
        return result

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def _render(
        self,
        output_path: Path,
        groups: SlotsByGroup,
        on_progress: Callable[[int, int], None] | None,
        mode: str,
        empty_message: str | None = None,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        c = canvas.Canvas(str(output_path), pagesize=A4)
        page_w_pt, page_h_pt = A4

        if not groups.groups:
            self._draw_empty_page(
                c, page_w_pt, page_h_pt, empty_message or "No hay cards para mostrar."
            )
            c.showPage()
            c.save()
            return

        total_slots = sum(len(slots) for _, _, slots in groups.groups)
        processed = 0
        cols = self.config.cols
        rows = self.config.rows
        slots_per_page = cols * rows

        margin_pt = MARGIN_MM * mm
        gap_pt = GAP_MM * mm
        header_h_pt = HEADER_H_MM * mm
        label_h_pt = LABEL_H_MM * mm
        footer_h_pt = FOOTER_H_MM * mm

        available_w = page_w_pt - 2 * margin_pt - (cols - 1) * gap_pt
        card_w = available_w / cols
        card_h = card_w * CARD_RATIO_H_OVER_W

        available_h = (
            page_h_pt
            - 2 * margin_pt
            - header_h_pt
            - footer_h_pt
            - rows * label_h_pt
            - (rows - 1) * gap_pt
        )
        max_card_h = available_h / rows
        if card_h > max_card_h:
            card_h = max_card_h
            card_w = card_h / CARD_RATIO_H_OVER_W

        page_num = 0
        for _, code_name, group_slots in groups.groups:
            slot_on_page = slots_per_page  # fuerza nueva página al inicio del grupo
            for slot in group_slots:
                if slot_on_page >= slots_per_page:
                    if processed > 0:
                        c.showPage()
                    page_num += 1
                    self._draw_group_header(
                        c, code_name, page_num, page_w_pt, page_h_pt, header_h_pt
                    )
                    self._draw_footer(c, page_w_pt, footer_h_pt)
                    slot_on_page = 0

                col = slot_on_page % cols
                row = slot_on_page // cols
                x = margin_pt + col * (card_w + gap_pt)
                y_top = (
                    page_h_pt
                    - margin_pt
                    - header_h_pt
                    - (row + 1) * card_h
                    - row * (label_h_pt + gap_pt)
                )

                badge = mode == "duplicates"
                self._draw_card_slot(
                    c,
                    x,
                    y_top,
                    card_w,
                    card_h,
                    label_h_pt,
                    slot,
                    show_badge=badge,
                    badge_count=max(0, slot.quantity - 1),
                )
                slot_on_page += 1
                processed += 1
                if on_progress is not None:
                    on_progress(processed, total_slots)
        c.showPage()
        c.save()

    def _draw_empty_page(
        self, c: canvas.Canvas, page_w: float, page_h: float, message: str
    ) -> None:
        c.setFont("Helvetica", 14)
        c.drawCentredString(page_w / 2, page_h / 2, message)

    def _draw_group_header(
        self,
        c: canvas.Canvas,
        group_name: str,
        page_num: int,
        page_w: float,
        page_h: float,
        header_h: float,
    ) -> None:
        margin_pt = MARGIN_MM * mm
        x0 = margin_pt
        y0 = page_h - margin_pt - header_h
        bar_w = page_w - 2 * margin_pt
        c.setFillColor(COLOR_HEADER_BG)
        c.rect(x0, y0, bar_w, header_h, stroke=0, fill=1)
        c.setFillColor(COLOR_HEADER_FG)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x0 + 4, y0 + header_h / 2 - 4, group_name)
        c.setFont("Helvetica", 9)
        c.drawRightString(x0 + bar_w - 4, y0 + header_h / 2 - 3, f"Pág. {page_num}")

    def _draw_footer(self, c: canvas.Canvas, page_w: float, footer_h: float) -> None:
        margin_pt = MARGIN_MM * mm
        c.setFillColor(COLOR_FOOTER_FG)
        c.setFont("Helvetica", 7)
        text = self.collection.collection_name + "  ·  " + format_for_display(utc_now())
        c.drawCentredString(page_w / 2, margin_pt + footer_h / 3, text)

    def _draw_card_slot(  # noqa: PLR0913 — geometría por argumentos
        self,
        c: canvas.Canvas,
        x: float,
        y: float,
        w: float,
        h: float,
        label_h: float,
        slot: CardSlotData,
        show_badge: bool,
        badge_count: int,
    ) -> None:
        # Fondo según estado
        bg_color = COLOR_OWNED_BG if slot.is_owned else COLOR_MISSING_BG
        c.setFillColor(bg_color)
        c.rect(x, y, w, h, stroke=0, fill=1)

        # Escudo (PNG con alpha) centrado
        crest = self._get_crest_image(slot.card.code_id)
        if crest is not None:
            crest_h = h * CREST_SCALE
            crest_w = crest_h
            cx = x + (w - crest_w) / 2
            cy = y + (h - crest_h) / 2 + label_h / 4  # leve offset hacia arriba
            try:
                c.drawImage(
                    crest,
                    cx,
                    cy,
                    width=crest_w,
                    height=crest_h,
                    preserveAspectRatio=True,
                    anchor="c",
                    mask="auto",
                )
            except Exception as exc:  # noqa: BLE001
                logger.debug("No se pudo dibujar escudo de %s: %s", slot.card.code_id, exc)

        # Línea separadora horizontal a 1/4 desde abajo
        sep_y = y + h * 0.22
        c.setStrokeColor(COLOR_SEPARATOR)
        c.setLineWidth(0.5)
        c.line(x + SEPARATOR_PAD_MM * mm, sep_y, x + w - SEPARATOR_PAD_MM * mm, sep_y)

        # Texto: #NUM NOMBRE bajo el separador
        c.setFillColor(COLOR_LABEL_FG)
        c.setFont("Helvetica-Bold", 7.5)
        label_text = (
            f"#{slot.card.card_number} {self._truncate(slot.card.card_name, MAX_NAME_CHARS)}"
        )
        c.drawCentredString(x + w / 2, y + h * 0.10, label_text)

        # Marco
        c.setStrokeColor(COLOR_BORDER)
        c.setLineWidth(0.5)
        c.rect(x, y, w, h, stroke=1, fill=0)

        # Label adicional debajo del slot (opcional, permite respiración)
        # — Mantenemos el label_h pero vacío para consistencia geométrica
        del label_h  # uso reservado para layout vertical, no dibujamos texto extra

        # Badge en esquina superior derecha (modo duplicates)
        if show_badge and badge_count > 0:
            badge_r = min(w, h) * 0.10
            cx_b = x + w - badge_r - 1
            cy_b = y + h - badge_r - 1
            c.setFillColor(COLOR_BADGE)
            c.circle(cx_b, cy_b, badge_r, stroke=0, fill=1)
            c.setFillColor(COLOR_BADGE_FG)
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(cx_b, cy_b - 2, f"x{badge_count}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_crest_image(self, code_id: str) -> ImageReader | None:
        """Carga (con cache por instancia) el escudo para un code_id."""
        if code_id in self._crest_cache:
            return self._crest_cache[code_id]
        path = get_crest_path(code_id)
        result: ImageReader | None
        if path.exists():
            try:
                result = ImageReader(str(path))
            except Exception as exc:  # noqa: BLE001
                logger.debug("ImageReader falló para %s: %s", path, exc)
                result = None
        else:
            result = None
        self._crest_cache[code_id] = result
        return result

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        text = text.upper()
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 1] + "…"

    def _format_list_header(
        self,
        title: str,
        count: int,
        total: int | None = None,
        kind: str = "faltantes",
    ) -> list[str]:
        sep = "═" * 35
        ts = format_for_display(utc_now(), with_seconds=True)
        if total is not None:
            count_line = f"Total {kind}: {count} / {total}"
        else:
            count_line = f"Total {kind}: {count}"
        return [
            sep,
            f"{title} — {self.collection.collection_name}",
            f"Generado: {ts}",
            count_line,
            sep,
        ]
