-- =========================================================
-- Migration 001 — Esquema inicial v0.2.0
-- =========================================================
-- Consolida todas las tablas del dominio aplicando las reglas de
-- CLAUDE.md sec 2:
--   - PKs subrogadas AUTOINCREMENT (sec 2.4)
--   - Business keys como UNIQUE constraint
--   - FKs granulares a la entidad atómica afectada (sec 2.5)
--   - Una sola fuente de verdad por dato (sec 2.6): inventory,
--     card_images y transactions referencian card_id, no
--     denormalizan collection_id/code_id/card_number
--   - card_images.image_path es la única fuente del path
--
-- Migración inmutable (sec 2.7). Todo cambio futuro va en una
-- migración nueva.

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------
-- Versionado del schema
-- ---------------------------------------------------------
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------
-- Settings clave/valor
-- ---------------------------------------------------------
CREATE TABLE app_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT
);

-- ---------------------------------------------------------
-- Universos de códigos
-- ---------------------------------------------------------
CREATE TABLE codes_headers (
    code_header_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_header_name TEXT NOT NULL UNIQUE,
    code_max_length INTEGER NOT NULL DEFAULT 5
);

-- ---------------------------------------------------------
-- Líneas de códigos (los códigos individuales de un universo)
-- ---------------------------------------------------------
CREATE TABLE codes_lines (
    code_line_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_header_id INTEGER NOT NULL,
    code_id TEXT NOT NULL,
    code_name TEXT NOT NULL,
    code_order INTEGER NOT NULL DEFAULT 0,
    UNIQUE (code_header_id, code_id),
    FOREIGN KEY (code_header_id) REFERENCES codes_headers(code_header_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_codes_lines_order
    ON codes_lines(code_header_id, code_order, code_id);

-- ---------------------------------------------------------
-- Colecciones
-- ---------------------------------------------------------
-- code_field_name: label visible del campo de código en la UI
--   (ej. "Set", "País"). NO es una "magic column" que indique
--   qué columna usar; es metadata de presentación.
-- album_*: layout del PDF álbum por colección.
CREATE TABLE collections (
    collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_name TEXT NOT NULL UNIQUE,
    card_count INTEGER NOT NULL,
    requires_code INTEGER NOT NULL DEFAULT 0,
    code_field_name TEXT,
    code_header_id INTEGER NOT NULL,
    is_premium INTEGER NOT NULL DEFAULT 0,
    license_key_required TEXT,
    album_columns INTEGER NOT NULL DEFAULT 3,
    album_rows INTEGER NOT NULL DEFAULT 4,
    album_orientation TEXT NOT NULL DEFAULT 'portrait'
        CHECK (album_orientation IN ('portrait', 'landscape')),
    FOREIGN KEY (code_header_id) REFERENCES codes_headers(code_header_id)
);

-- ---------------------------------------------------------
-- Catálogo de cards (PK subrogada + UNIQUE business key)
-- ---------------------------------------------------------
CREATE TABLE cards (
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    code_id TEXT NOT NULL,
    card_number INTEGER NOT NULL,
    card_name TEXT NOT NULL,
    UNIQUE (collection_id, code_id, card_number),
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_cards_collection ON cards(collection_id);

-- ---------------------------------------------------------
-- Inventario del usuario (1:1 con cards via card_id UNIQUE)
-- ---------------------------------------------------------
CREATE TABLE inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL UNIQUE,
    quantity INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (card_id) REFERENCES cards(card_id)
        ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- Tracking de imágenes generadas (1:1 con cards)
-- Única fuente del path de imagen.
-- ---------------------------------------------------------
CREATE TABLE card_images (
    card_image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL UNIQUE,
    found_photo INTEGER NOT NULL DEFAULT 0,
    image_source TEXT,
    image_path TEXT,
    generated_at TEXT,
    FOREIGN KEY (card_id) REFERENCES cards(card_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_card_images_found ON card_images(found_photo);

-- ---------------------------------------------------------
-- Bitácora de operaciones (alta/baja)
-- FK granular a card_id (sec 2.5).
-- exchange_event_id agrupa transacciones que pertenecen a un
-- mismo intercambio (mismo identificador en todas las bajas y
-- altas del evento). NULL para transacciones que no son parte
-- de un intercambio.
-- ---------------------------------------------------------
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER NOT NULL,
    operation TEXT NOT NULL CHECK (operation IN ('alta', 'baja')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    transaction_date TEXT NOT NULL DEFAULT (datetime('now')),
    exchange_event_id INTEGER,
    FOREIGN KEY (card_id) REFERENCES cards(card_id)
);

CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_card ON transactions(card_id);
CREATE INDEX idx_transactions_exchange_event
    ON transactions(exchange_event_id);

-- ---------------------------------------------------------
-- Marcar esta migración como aplicada
-- ---------------------------------------------------------
INSERT INTO schema_version (version) VALUES (1);
