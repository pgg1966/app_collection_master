"""Generadores de PDF: álbum visual + listas (faltantes/repetidas/lo que tengo).

API funcional, sin estado: cada `generate_*_pdf(...)` recibe los datos ya
resueltos (vía `AlbumService.build_album_cards`) y escribe el PDF en
`output_path`.

Layout del álbum visual:
- A4 (portrait o landscape según `Collection.album_orientation`).
- Grilla configurable por colección (`album_columns × album_rows`),
  default 3×4 portrait = 12 cards/hoja A4.
- Cada `code_id` arranca en página nueva con header oscuro de categoría.
- Celdas:
  * CASO A — con imagen (foto descargada por scraper Panini): se dibuja.
  * CASO B — sin imagen, en inventario: rectángulo celeste + texto.
  * CASO C — sin imagen, no en inventario: rectángulo blanco + borde gris.
- Badge ×N en esquina superior derecha si `quantity > 1`.

PDFs de lista (faltantes / repetidas / owned):
- Texto puro Helvetica 9pt, 2 columnas por página.
- Header global (nombre colección, tipo, fecha) en primera página.
- Header de categoría cuando cambia `code_id`.
- Metadata de intercambio embebida en `Subject` + `Keywords` con
  checksum SHA256 truncado para detectar manipulaciones.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from itertools import groupby
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from collections_app.core.models import Card, Collection

logger = logging.getLogger(__name__)

# Geometría base
MARGIN_PT = 28.35  # 10mm
HEADER_PT = 22.68  # 8mm
CELL_PADDING_PT = 2.84  # 1mm
LIST_LINE_HEIGHT_PT = 13.0
LIST_COL_GAP_PT = 14.0
LIST_HEADER_FONT_SIZE = 14
LIST_BODY_FONT_SIZE = 9
ALBUM_CELL_NUM_FONT_SIZE = 9
ALBUM_CELL_NAME_FONT_SIZE = 8
ALBUM_CELL_CODE_FONT_SIZE = 7
ALBUM_HEADER_FONT_SIZE = 10
ALBUM_PAGE_NUM_FONT_SIZE = 7

# Colores
COLOR_CELESTE = Color(174 / 255, 214 / 255, 241 / 255)
COLOR_WHITE = Color(1.0, 1.0, 1.0)
COLOR_GRAY_BORDER = Color(0.67, 0.67, 0.67)
COLOR_HEADER_BG = Color(0.2, 0.2, 0.2)
COLOR_HEADER_FG = white
COLOR_DARK_TEXT = Color(0.15, 0.15, 0.15)
COLOR_BADGE_BG = COLOR_CELESTE
COLOR_BADGE_FG = white
COLOR_PAGE_NUM_FG = Color(0.5, 0.5, 0.5)
COLOR_LIST_SEPARATOR = HexColor("#d0d0d0")
COLOR_LIST_CATEGORY_FG = Color(0.1, 0.1, 0.1)

# Constantes de metadata de intercambio
EXCHANGE_APP_NAME = "CollectionsApp"
EXCHANGE_PROTOCOL_VERSION = "1.0"
EXCHANGE_CHECKSUM_LEN = 16

MAX_NAME_CHARS = 20


# ----------------------------------------------------------------------
# Modelos de input / output
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class AlbumCard:
    """Una card del álbum con su contexto enriquecido para renderear.

    `image_path` es `None` si la imagen no está descargada todavía. En ese
    caso se usa placeholder celeste (si `quantity > 0`) o blanco.

    `code_order` es la posición de la categoría dentro del header (ver
    `CodeLine.code_order`). El renderer lo usa para mostrar las categorías
    en el orden definido por el admin, no en orden alfabético del code_id.
    """

    card: Card
    quantity: int
    image_path: Path | None
    requires_code: bool
    code_name: str  # nombre humano del código (ej. "ARGENTINA")
    code_order: int = 0  # default 0 → cae al final si está sin ordenar


@dataclass
class PdfGeneratorResult:
    """Resumen del PDF generado."""

    pages: int = 0
    cards_with_image: int = 0
    cards_celeste_placeholder: int = 0
    cards_missing: int = 0
    output_path: Path = field(default_factory=Path)


# ----------------------------------------------------------------------
# Helpers de label / chunks
# ----------------------------------------------------------------------


def format_label(card_number: int, code_id: str, requires_code: bool) -> str:
    """`requires_code=True` → 'ARG-5'; sino → '5'."""
    if requires_code:
        return f"{code_id}-{card_number}"
    return str(card_number)


def _chunks(items: list[AlbumCard], size: int) -> list[list[AlbumCard]]:
    """Parte `items` en grupos de `size`. El último puede ser más chico."""
    if size <= 0:
        return []
    return [items[i : i + size] for i in range(0, len(items), size)]


def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


# ----------------------------------------------------------------------
# Metadata de intercambio
# ----------------------------------------------------------------------


def _build_exchange_metadata(
    subtype: str,
    collection_id: int,
    collection_name: str,
    cards: list[dict[str, object]],
) -> str:
    """Construye el JSON de metadata embebida en PDFs de lista.

    El checksum es un SHA256 truncado a `EXCHANGE_CHECKSUM_LEN` chars,
    calculado sobre los campos estables (excluyendo `generated_at` para
    que el PDF sea reproducible bit-a-bit dado el mismo input). La idea
    es que la futura función "Intercambio" pueda detectar PDFs manipulados.
    """
    payload: dict[str, object] = {
        "app": EXCHANGE_APP_NAME,
        "version": EXCHANGE_PROTOCOL_VERSION,
        "type": "exchange",
        "subtype": subtype,
        "collection_id": collection_id,
        "collection_name": collection_name,
        "generated_at": datetime.now(UTC).isoformat(),
        "cards": cards,
    }
    base = json.dumps(
        {k: v for k, v in payload.items() if k != "generated_at"},
        sort_keys=True,
        ensure_ascii=False,
    )
    payload["checksum"] = hashlib.sha256(base.encode("utf-8")).hexdigest()[:EXCHANGE_CHECKSUM_LEN]
    return json.dumps(payload, ensure_ascii=False)


def validate_exchange_pdf_metadata(pdf_path: Path) -> dict[str, object] | None:
    """Lee la metadata de intercambio de un PDF generado por CollectionsApp.

    Retorna el dict si el checksum es válido, `None` si:
    - no es un PDF de CollectionsApp (no tiene la metadata o `app != ...`),
    - el JSON está corrupto,
    - el checksum no matchea (PDF manipulado).
    """
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf_path))
        if reader.metadata is None:
            return None
        keywords = reader.metadata.get("/Keywords", "")
        if not keywords:
            return None
        data = json.loads(keywords)
    except Exception as exc:  # noqa: BLE001
        logger.debug("validate_exchange_pdf_metadata: parsing falló: %s", exc)
        return None

    if not isinstance(data, dict) or data.get("app") != EXCHANGE_APP_NAME:
        return None

    stored_checksum = data.get("checksum")
    if not isinstance(stored_checksum, str):
        return None

    base = json.dumps(
        {k: v for k, v in data.items() if k not in ("checksum", "generated_at")},
        sort_keys=True,
        ensure_ascii=False,
    )
    computed = hashlib.sha256(base.encode("utf-8")).hexdigest()[:EXCHANGE_CHECKSUM_LEN]
    if computed != stored_checksum:
        return None
    return data


# ----------------------------------------------------------------------
# Render de álbum visual
# ----------------------------------------------------------------------


def generate_album_pdf(
    collection: Collection,
    album_cards: list[AlbumCard],
    output_path: Path,
) -> PdfGeneratorResult:
    """Genera el PDF álbum visual (todas las cards, foto o placeholder).

    Cada `code_id` empieza en página nueva con header oscuro. Layout
    `album_columns × album_rows` desde `collection`.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pagesize = landscape(A4) if collection.album_orientation == "landscape" else A4
    page_w, page_h = pagesize
    cols = max(1, collection.album_columns)
    rows = max(1, collection.album_rows)
    cell_w, cell_h = _cell_geometry(page_w, page_h, cols, rows)

    c = canvas.Canvas(str(output_path), pagesize=pagesize)
    result = PdfGeneratorResult(output_path=output_path)

    if not album_cards:
        c.setFont("Helvetica", 14)
        c.drawCentredString(page_w / 2, page_h / 2, "(sin cards para mostrar)")
        c.showPage()
        c.save()
        result.pages = 1
        return result

    # Agrupar por code_id manteniendo el orden de entrada.
    grouped = groupby(album_cards, key=lambda ac: ac.card.code_id)
    page_num = 0
    for _, items_iter in grouped:
        items = list(items_iter)
        code_name = items[0].code_name
        for chunk in _chunks(items, cols * rows):
            page_num += 1
            _draw_album_header(c, code_name, page_w, page_h)
            _draw_page_number(c, page_num, page_w)
            for idx, ac in enumerate(chunk):
                col_i = idx % cols
                row_i = idx // cols
                x, y = _cell_origin(col_i, row_i, cell_w, cell_h, page_h)
                _draw_album_cell(c, ac, x, y, cell_w, cell_h, result)
            c.showPage()

    c.save()
    result.pages = page_num
    return result


def _cell_geometry(page_w: float, page_h: float, cols: int, rows: int) -> tuple[float, float]:
    """Ancho/alto de cada celda dado el espacio útil de la página."""
    usable_w = page_w - 2 * MARGIN_PT
    usable_h = page_h - 2 * MARGIN_PT - HEADER_PT
    return usable_w / cols, usable_h / rows


def _cell_origin(
    col_i: int, row_i: int, cell_w: float, cell_h: float, page_h: float
) -> tuple[float, float]:
    """Esquina inferior-izquierda de una celda en coords reportlab."""
    x = MARGIN_PT + col_i * cell_w
    y = page_h - MARGIN_PT - HEADER_PT - (row_i + 1) * cell_h
    return x, y


def _draw_album_header(c: canvas.Canvas, text: str, page_w: float, page_h: float) -> None:
    x = MARGIN_PT
    y = page_h - MARGIN_PT - HEADER_PT
    bar_w = page_w - 2 * MARGIN_PT
    c.setFillColor(COLOR_HEADER_BG)
    c.rect(x, y, bar_w, HEADER_PT, stroke=0, fill=1)
    c.setFillColor(COLOR_HEADER_FG)
    c.setFont("Helvetica-Bold", ALBUM_HEADER_FONT_SIZE)
    c.drawCentredString(page_w / 2, y + HEADER_PT / 2 - 4, text.upper())


def _draw_page_number(c: canvas.Canvas, page_num: int, page_w: float) -> None:
    c.setFillColor(COLOR_PAGE_NUM_FG)
    c.setFont("Helvetica", ALBUM_PAGE_NUM_FONT_SIZE)
    c.drawCentredString(page_w / 2, MARGIN_PT / 2, str(page_num))


def _draw_album_cell(
    c: canvas.Canvas,
    ac: AlbumCard,
    x: float,
    y: float,
    w: float,
    h: float,
    result: PdfGeneratorResult,
) -> None:
    """Dibuja una celda según el caso (A/B/C) y actualiza contadores.

    REGLA IMPORTANTE: la foto solo se dibuja si la card está en inventario
    (`quantity > 0`). Si no la tengo, siempre va al placeholder blanco —
    aunque la foto exista en disco — porque el álbum representa MI
    colección, no el catálogo.
    """
    inner_x = x + CELL_PADDING_PT
    inner_y = y + CELL_PADDING_PT
    inner_w = w - 2 * CELL_PADDING_PT
    inner_h = h - 2 * CELL_PADDING_PT

    if ac.quantity > 0 and ac.image_path is not None and ac.image_path.exists():
        # CASO A: tengo la card y hay foto descargada → mostrar foto
        try:
            img = ImageReader(str(ac.image_path))
            c.drawImage(
                img,
                inner_x,
                inner_y,
                width=inner_w,
                height=inner_h,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto",
            )
            result.cards_with_image += 1
        except Exception as exc:  # noqa: BLE001
            logger.debug("Falló drawImage para card %s: %s", ac.card.card_number, exc)
            _draw_placeholder_cell(c, ac, inner_x, inner_y, inner_w, inner_h)
            result.cards_celeste_placeholder += 1
    elif ac.quantity > 0:
        # CASO B: tengo la card pero sin foto → placeholder celeste
        _draw_placeholder_cell(c, ac, inner_x, inner_y, inner_w, inner_h)
        result.cards_celeste_placeholder += 1
    else:
        # CASO C: NO la tengo → placeholder blanco con borde gris.
        # Aunque la foto esté en disco, no se muestra: el álbum
        # representa la colección del usuario, no el catálogo.
        _draw_placeholder_cell(c, ac, inner_x, inner_y, inner_w, inner_h)
        result.cards_missing += 1

    if ac.quantity > 1:
        _draw_quantity_badge(c, ac.quantity, x + w, y + h)


def _draw_placeholder_cell(
    c: canvas.Canvas, ac: AlbumCard, x: float, y: float, w: float, h: float
) -> None:
    """Rectángulo celeste (en inventario) o blanco con borde (no inventario)."""
    if ac.quantity > 0:
        c.setFillColor(COLOR_CELESTE)
        c.rect(x, y, w, h, stroke=0, fill=1)
    else:
        c.setFillColor(COLOR_WHITE)
        c.setStrokeColor(COLOR_GRAY_BORDER)
        c.setLineWidth(1)
        c.rect(x, y, w, h, stroke=1, fill=1)

    # Texto centrado: número/código-número (bold), nombre, code_id
    cx = x + w / 2
    cy = y + h / 2
    label = format_label(ac.card.card_number, ac.card.code_id, ac.requires_code)
    name = _truncate(ac.card.card_name, MAX_NAME_CHARS)

    c.setFillColor(COLOR_DARK_TEXT)
    c.setFont("Helvetica-Bold", ALBUM_CELL_NUM_FONT_SIZE)
    c.drawCentredString(cx, cy + 8, label)
    c.setFont("Helvetica", ALBUM_CELL_NAME_FONT_SIZE)
    c.drawCentredString(cx, cy - 2, name)
    c.setFont("Helvetica", ALBUM_CELL_CODE_FONT_SIZE)
    c.drawCentredString(cx, cy - 12, ac.card.code_id)


def _draw_quantity_badge(
    c: canvas.Canvas, quantity: int, top_right_x: float, top_right_y: float
) -> None:
    """Círculo celeste con número blanco en esquina superior derecha."""
    radius = 7.0
    cx = top_right_x - radius - 1
    cy = top_right_y - radius - 1
    c.setFillColor(COLOR_BADGE_BG)
    c.circle(cx, cy, radius, stroke=0, fill=1)
    c.setFillColor(COLOR_BADGE_FG)
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(cx, cy - 2, f"×{quantity}")


# ----------------------------------------------------------------------
# Render de PDFs de lista (faltantes / repetidas / owned)
# ----------------------------------------------------------------------


def generate_missing_pdf(
    collection: Collection,
    album_cards: list[AlbumCard],
    output_path: Path,
) -> PdfGeneratorResult:
    """PDF de cards que faltan (`quantity == 0`)."""
    missing = [ac for ac in album_cards if ac.quantity == 0]
    return _generate_list_pdf(
        collection, missing, output_path, subtype="missing", title="Faltantes"
    )


def generate_duplicates_pdf(
    collection: Collection,
    album_cards: list[AlbumCard],
    output_path: Path,
) -> PdfGeneratorResult:
    """PDF de cards repetidas (`quantity > 1`) con columna ×N."""
    dups = [ac for ac in album_cards if ac.quantity > 1]
    return _generate_list_pdf(
        collection,
        dups,
        output_path,
        subtype="duplicates",
        title="Repetidas",
        show_quantity=True,
    )


def generate_owned_pdf(
    collection: Collection,
    album_cards: list[AlbumCard],
    output_path: Path,
) -> PdfGeneratorResult:
    """PDF de cards en posesión (`quantity >= 1`)."""
    owned = [ac for ac in album_cards if ac.quantity >= 1]
    return _generate_list_pdf(collection, owned, output_path, subtype="owned", title="Lo que tengo")


def _generate_list_pdf(
    collection: Collection,
    items: list[AlbumCard],
    output_path: Path,
    subtype: str,
    title: str,
    show_quantity: bool = False,
) -> PdfGeneratorResult:
    """Helper: layout 2 columnas con header global + categorías + items."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = A4
    c = canvas.Canvas(str(output_path), pagesize=A4)

    # Metadata embebida (futura función intercambio)
    assert collection.collection_id is not None
    cards_meta: list[dict[str, object]] = [
        {
            "code_id": ac.card.code_id,
            "card_number": ac.card.card_number,
            "quantity": ac.quantity,
        }
        for ac in items
    ]
    metadata_json = _build_exchange_metadata(
        subtype=subtype,
        collection_id=collection.collection_id,
        collection_name=collection.collection_name,
        cards=cards_meta,
    )
    c.setSubject("CollectionsApp Exchange Data")
    c.setKeywords(metadata_json)
    c.setCreator(EXCHANGE_APP_NAME)

    # Layout
    col_w = (page_w - 2 * MARGIN_PT - LIST_COL_GAP_PT) / 2
    column_xs = (MARGIN_PT, MARGIN_PT + col_w + LIST_COL_GAP_PT)

    # Cursor: y arranca debajo del header global
    y = page_h - MARGIN_PT
    y = _draw_list_global_header(c, collection, title, items, page_w, y)
    y_top_after_global = y  # primera columna arranca acá
    col_idx = 0
    page_num = 1
    result = PdfGeneratorResult(output_path=output_path, pages=1)

    if not items:
        c.setFont("Helvetica", 11)
        c.drawCentredString(page_w / 2, page_h / 2, f"(no hay {title.lower()})")
        c.showPage()
        c.save()
        return result

    def new_column() -> None:
        nonlocal col_idx, y, page_num
        col_idx += 1
        if col_idx >= 2:
            c.showPage()
            page_num += 1
            result.pages = page_num
            col_idx = 0
            y = page_h - MARGIN_PT
        else:
            y = y_top_after_global

    def ensure_room(needed: float) -> None:
        nonlocal y
        if y - needed < MARGIN_PT:
            new_column()

    # Iterar agrupado por code_id; al cambiar, escribir header de categoría.
    last_code: str | None = None
    for ac in items:
        if ac.card.code_id != last_code:
            ensure_room(LIST_LINE_HEIGHT_PT * 2)
            _draw_category_header(c, ac.card.code_id, ac.code_name, column_xs[col_idx], y, col_w)
            y -= LIST_LINE_HEIGHT_PT * 1.4
            last_code = ac.card.code_id

        ensure_room(LIST_LINE_HEIGHT_PT)
        _draw_list_item(
            c,
            ac,
            column_xs[col_idx],
            y,
            col_w,
            show_quantity=show_quantity,
        )
        y -= LIST_LINE_HEIGHT_PT

        # Contadores
        if ac.quantity == 0:
            result.cards_missing += 1
        elif ac.image_path is not None and ac.image_path.exists():
            result.cards_with_image += 1
        else:
            result.cards_celeste_placeholder += 1

    # Total al pie
    ensure_room(LIST_LINE_HEIGHT_PT * 3)
    _draw_list_total(c, items, title, column_xs[col_idx], y, col_w, show_quantity)

    c.showPage()
    c.save()
    return result


def _draw_list_global_header(
    c: canvas.Canvas,
    collection: Collection,
    title: str,
    items: list[AlbumCard],
    page_w: float,
    y_top: float,
) -> float:
    del items  # firmado por simetría con futuras variantes
    x_left = MARGIN_PT
    x_right = page_w - MARGIN_PT
    y = y_top - LIST_HEADER_FONT_SIZE
    c.setFillColor(COLOR_DARK_TEXT)
    c.setFont("Helvetica-Bold", LIST_HEADER_FONT_SIZE)
    c.drawString(x_left, y, collection.collection_name)
    y -= LIST_LINE_HEIGHT_PT
    c.setFont("Helvetica", LIST_BODY_FONT_SIZE)
    c.drawString(x_left, y, title)
    y -= LIST_LINE_HEIGHT_PT * 0.85
    c.setFont("Helvetica", 8)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.drawString(x_left, y, f"Generado: {ts}")
    # separador horizontal
    y -= 6
    c.setStrokeColor(COLOR_LIST_SEPARATOR)
    c.setLineWidth(0.5)
    c.line(x_left, y, x_right, y)
    y -= LIST_LINE_HEIGHT_PT
    return y


def _draw_category_header(
    c: canvas.Canvas, code_id: str, code_name: str, x: float, y: float, col_w: float
) -> None:
    c.setFillColor(COLOR_LIST_CATEGORY_FG)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x, y, f"▶ {code_name.upper()} ({code_id})")
    c.setStrokeColor(COLOR_LIST_SEPARATOR)
    c.setLineWidth(0.4)
    c.line(x, y - 2, x + col_w, y - 2)


def _draw_list_item(
    c: canvas.Canvas,
    ac: AlbumCard,
    x: float,
    y: float,
    col_w: float,
    show_quantity: bool,
) -> None:
    label = format_label(ac.card.card_number, ac.card.code_id, ac.requires_code)
    name = _truncate(ac.card.card_name, 32)
    c.setFillColor(COLOR_DARK_TEXT)
    c.setFont("Helvetica", LIST_BODY_FONT_SIZE)
    # Columna izquierda: label en ancho fijo de ~40pt, alineado a la derecha.
    label_x = x + 40
    c.drawRightString(label_x, y, label)
    c.drawString(label_x + 6, y, name)
    if show_quantity:
        c.drawRightString(x + col_w, y, f"×{ac.quantity}")


def _draw_list_total(
    c: canvas.Canvas,
    items: list[AlbumCard],
    title: str,
    x: float,
    y: float,
    col_w: float,
    show_quantity: bool,
) -> None:
    y -= LIST_LINE_HEIGHT_PT
    c.setStrokeColor(COLOR_LIST_SEPARATOR)
    c.setLineWidth(0.5)
    c.line(x, y, x + col_w, y)
    y -= LIST_LINE_HEIGHT_PT
    c.setFillColor(COLOR_DARK_TEXT)
    c.setFont("Helvetica-Bold", LIST_BODY_FONT_SIZE)
    n = len(items)
    if show_quantity:
        units = sum(ac.quantity for ac in items)
        c.drawString(x, y, f"Total {title.lower()}: {n}, total unidades: {units}")
    else:
        c.drawString(x, y, f"Total {title.lower()}: {n}")
