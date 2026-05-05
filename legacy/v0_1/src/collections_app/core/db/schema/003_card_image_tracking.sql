-- =========================================================
-- Migration 003 — Tracking de imágenes generadas por card
-- =========================================================
--
-- Reemplaza el `_index.json` por persistencia en DB. Cada fila guarda
-- si la card terminó con foto real (`found_photo=1`) o placeholder (0),
-- la fuente de la foto, y la fecha de generación. El borrado en cascada
-- desde `cards` mantiene esta tabla consistente cuando se elimina una
-- colección.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS card_images (
    collection_id INTEGER NOT NULL,
    code_id TEXT NOT NULL,
    card_number INTEGER NOT NULL,
    found_photo INTEGER NOT NULL DEFAULT 0,  -- bool: 1=foto real, 0=placeholder
    image_source TEXT,     -- 'wikipedia' | 'duckduckgo' | 'google' | 'placeholder' | 'cache'
    image_path TEXT,       -- path al PNG generado
    generated_at TEXT,     -- ISO datetime UTC
    PRIMARY KEY (collection_id, code_id, card_number),
    FOREIGN KEY (collection_id, code_id, card_number)
        REFERENCES cards(collection_id, code_id, card_number)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_card_images_found
    ON card_images(collection_id, found_photo);

INSERT INTO schema_version (version) VALUES (3);
