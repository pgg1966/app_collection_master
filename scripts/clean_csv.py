"""Limpia CSVs antes de importar al sistema.

Aplica en orden:
1. Repara mojibake UTF-8 leído como Latin-1 (`Ã©` → `é`, `Ã±` → `ñ`).
2. Strip de acentos preservando `ñ`/`Ñ` (`JIMÉNEZ` → `JIMENEZ`,
   `MUÑOZ` → `MUÑOZ`).
3. Normaliza chars nórdicos/germánicos sin equivalente NFD
   (`ø`→`o`, `å`→`a`, `ß`→`ss`, `æ`→`ae`).
4. Convierte a MAYÚSCULAS.
5. Trim de espacios en cada celda.
6. Cambia separador `;` por `,`.
7. Filtra filas vacías y filas con `card_number` negativo (el importer
   acepta 0 — útil para tarjeta-portada del álbum).

Uso:
    python scripts/clean_csv.py <archivo_in.csv> <archivo_out.csv>

El script no valida formato — solo limpia. Las validaciones (códigos
existentes, números positivos, nombres no vacíos) corren después en el
importer mismo.
"""

import sys
import unicodedata
from pathlib import Path

# Chars que NFD no descompone (no son letra+combining). Los mapeamos
# explícitamente porque suelen aparecer en nombres nórdicos / alemanes.
EXTRA_NORMALIZE = {
    "ø": "o",
    "Ø": "O",
    "å": "a",
    "Å": "A",
    "æ": "ae",
    "Æ": "AE",
    "ß": "ss",
    "ð": "d",
    "Ð": "D",
    "þ": "th",
    "Þ": "TH",
    "đ": "d",
    "Đ": "D",
    "ł": "l",
    "Ł": "L",
}


def fix_mojibake(text: str) -> str:
    """Repara doble-codificación UTF-8 → CP1252/Latin-1.

    Probamos primero cp1252 (típico en Windows: incluye ‘ ’ € ‰ … en
    el rango 0x80-0x9F, donde Latin-1 tiene slots vacíos). Si cp1252
    falla, probamos Latin-1 puro. Si ambos fallan o el resultado no
    es UTF-8 válido, devolvemos el texto original.
    """
    for encoding in ("cp1252", "latin-1"):
        try:
            return text.encode(encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    return text


def strip_accents_keep_n(text: str) -> str:
    """Quita acentos pero preserva la `ñ`/`Ñ`."""
    # Reservar ñ/Ñ con placeholders que NFD no toca
    placeholders = {"ñ": "\x01", "Ñ": "\x02"}
    for src, ph in placeholders.items():
        text = text.replace(src, ph)

    # NFD descompone "é" → "e" + "´"; filtrar combining marks
    nfd = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")

    # Aplicar mapeo de chars que NFD no descompone (ø, å, ß, æ, …)
    for src, dst in EXTRA_NORMALIZE.items():
        stripped = stripped.replace(src, dst)

    # Restaurar ñ/Ñ
    for src, ph in placeholders.items():
        stripped = stripped.replace(ph, src)

    return stripped


def clean_cell(cell: str) -> str:
    """Aplica fix_mojibake → strip_accents → uppercase → trim."""
    cell = fix_mojibake(cell)
    cell = strip_accents_keep_n(cell)
    cell = cell.upper().strip()
    return cell


def clean_file(input_path: Path, output_path: Path) -> tuple[int, int]:
    """Lee `input_path` y escribe `output_path` limpio.

    Detecta separador (`;` o `,`) en la primera línea no vacía.
    Skips filas donde card_number ≤ 0 (segunda columna).

    Returns:
        (filas_leidas, filas_escritas)
    """
    # Probar UTF-8 primero (formato más común). Si falla, usar Latin-1
    # como fallback (tolera cualquier byte). En ambos casos `fix_mojibake`
    # reparará los chars que estaban doble-codificados.
    raw_bytes = input_path.read_bytes()
    try:
        raw_text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raw_text = raw_bytes.decode("latin-1", errors="replace")
    lines = raw_text.splitlines()

    # Strip BOM si está presente
    if lines and lines[0].startswith("﻿"):
        lines[0] = lines[0][1:]
    if lines and lines[0].startswith("ï»¿"):
        # BOM UTF-8 mojibake leído como Latin-1
        lines[0] = lines[0][3:]

    # Detectar separador en la primera línea
    first_non_empty = next((line for line in lines if line.strip()), "")
    sep = ";" if first_non_empty.count(";") > first_non_empty.count(",") else ","

    output_lines: list[str] = []
    rows_read = 0
    rows_written = 0
    for raw_line in lines:
        if not raw_line.strip():
            continue
        rows_read += 1
        cells = [clean_cell(c) for c in raw_line.split(sep)]

        # Si parece la fila header, mantenerla
        is_header = cells and cells[0] in {"CODE_ID"}

        # Para filas de cards (3 cols con segundo numérico), skip si number < 0
        if not is_header and len(cells) >= 3:
            try:
                num = int(cells[1])
                if num < 0:
                    continue
            except ValueError:
                # No es card; podría ser code line con order. Dejar pasar.
                pass

        output_lines.append(",".join(cells))
        rows_written += 1

    output_path.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    return rows_read, rows_written


def main() -> int:
    if len(sys.argv) != 3:
        print(f"uso: python {sys.argv[0]} <input.csv> <output.csv>", file=sys.stderr)
        return 2
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    if not input_path.exists():
        print(f"error: no existe {input_path}", file=sys.stderr)
        return 1
    rows_read, rows_written = clean_file(input_path, output_path)
    print(f"OK: {input_path.name} -> {output_path.name} ({rows_read} -> {rows_written} filas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
