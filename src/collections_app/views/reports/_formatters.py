"""Algoritmos puros para los reportes de WhatsApp.

Funciones sin Qt, testeables sin display. La UI las consume y pasa
los strings al panel de exportación.

**Reglas de formato (del prompt 4b):**

- Una línea por código que tenga ≥1 entrada en la categoría.
- Códigos sin entradas → omitidos (no aparece "FRANCIA: " si no falta nada).
- Números separados por `" - "` (espacio guion espacio).
- Repetidas: `<num> (x<extra>)` donde `extra = quantity - 1`.
- Orden: respeta `code_order` del CodeHeader.
- `code_name` se usa tal cual de la DB (sin uppercase, sin traducción).

**Helper de exportación**:

- `text_fits_in_url(text, limit=URL_SAFE_LIMIT)`: True si el texto cabe
  en un URL de mailto/wa.me sin riesgo de truncamiento. 1500 chars es
  un límite seguro empírico (menor al 2083 de IE / mayor al límite de
  WhatsApp Web).
"""

from __future__ import annotations

from collections import defaultdict

from collections_app.core.models.card import Card
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.inventory_item import InventoryItem

URL_SAFE_LIMIT = 1500


def format_missing_report(
    missing_cards: list[Card],
    codes_in_order: list[CodeLine],
) -> str:
    """Genera el texto de faltantes.

    Una línea por code (en orden de `code_order`) con los `card_number`
    de las cards faltantes en ese code, separados por `" - "`. Codes
    sin faltantes NO aparecen en el output.

    Args:
        missing_cards: cards que el usuario aún no tiene (qty=0 o sin
            entry en inventory).
        codes_in_order: `code_lines` del header de la colección, ya
            ordenadas como las quiere ver el usuario.

    Returns:
        Texto plano. Vacío si no hay faltantes.
    """
    by_code: dict[str, list[int]] = defaultdict(list)
    for card in missing_cards:
        by_code[card.code_id].append(card.card_number)

    lines: list[str] = []
    for code_line in codes_in_order:
        numbers = sorted(by_code.get(code_line.code_id, []))
        if not numbers:
            continue
        nums_text = " - ".join(str(n) for n in numbers)
        lines.append(f"{code_line.code_name}: {nums_text}")
    return "\n".join(lines)


def format_duplicates_report(
    duplicates: list[InventoryItem],
    cards_by_id: dict[int, Card],
    codes_in_order: list[CodeLine],
) -> str:
    """Genera el texto de repetidas.

    Una línea por code con cada `<card_number> (x<extra>)` donde
    `extra = quantity - 1`. Solo entradas con `quantity > 1` se incluyen.

    Args:
        duplicates: inventory items con `quantity > 1`.
        cards_by_id: dict de Card por card_id (para resolver code_id +
            card_number desde el inventory item).
        codes_in_order: code_lines en orden visual.

    Returns:
        Texto plano. Vacío si no hay repetidas.
    """
    by_code: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for item in duplicates:
        if item.quantity <= 1:
            continue
        card = cards_by_id.get(item.card_id)
        if card is None:
            continue
        extra = item.quantity - 1
        by_code[card.code_id].append((card.card_number, extra))

    lines: list[str] = []
    for code_line in codes_in_order:
        entries = sorted(by_code.get(code_line.code_id, []))
        if not entries:
            continue
        parts = [f"{num} (x{extra})" for num, extra in entries]
        lines.append(f"{code_line.code_name}: {' - '.join(parts)}")
    return "\n".join(lines)


def text_fits_in_url(text: str, limit: int = URL_SAFE_LIMIT) -> bool:
    """True si el texto cabe en un URL de share (mailto/wa.me) sin riesgo.

    Empírico: 1500 chars es seguro para mailto en Outlook/Gmail clients
    y para `wa.me/?text=` en WhatsApp Web. Por encima, el SO o el
    cliente puede truncar silenciosamente.
    """
    return len(text) <= limit
