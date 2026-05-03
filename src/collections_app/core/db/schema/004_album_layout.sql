-- =========================================================
-- Migration 004 — Layout configurable de álbum por colección
-- =========================================================
--
-- Cada colección define su propio layout de PDF álbum:
-- - `album_columns`: cards por fila (ej. 3, 4)
-- - `album_rows`: filas por página (ej. 4, 3)
-- - `album_orientation`: 'portrait' o 'landscape' — algunas colecciones
--   tienen cards horizontales y necesitan landscape para que entren bien.
--
-- Defaults razonables: 3 cols × 4 rows portrait (12 cards/hoja A4).
-- Las colecciones existentes los reciben automáticamente.

PRAGMA foreign_keys = ON;

ALTER TABLE collections ADD COLUMN album_columns INTEGER NOT NULL DEFAULT 3;
ALTER TABLE collections ADD COLUMN album_rows INTEGER NOT NULL DEFAULT 4;
ALTER TABLE collections ADD COLUMN album_orientation TEXT NOT NULL DEFAULT 'portrait'
    CHECK (album_orientation IN ('portrait', 'landscape'));

INSERT INTO schema_version (version) VALUES (4);
