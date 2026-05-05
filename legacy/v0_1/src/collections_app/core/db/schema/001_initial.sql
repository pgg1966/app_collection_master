-- =========================================================
-- Migration 001 — Esquema inicial
-- =========================================================

PRAGMA foreign_keys = ON;

-- Versionado del schema
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Settings clave/valor
CREATE TABLE IF NOT EXISTS app_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT
);

-- Headers de codigos (universos de codigos)
CREATE TABLE IF NOT EXISTS codes_headers (
    code_header_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_header_name TEXT NOT NULL UNIQUE,
    code_max_length INTEGER NOT NULL DEFAULT 5
);

-- Lineas de codigos (los codigos individuales)
CREATE TABLE IF NOT EXISTS codes_lines (
    code_header_id INTEGER NOT NULL,
    code_id TEXT NOT NULL,
    code_name TEXT NOT NULL,
    PRIMARY KEY (code_header_id, code_id),
    FOREIGN KEY (code_header_id) REFERENCES codes_headers(code_header_id)
        ON DELETE CASCADE
);

-- Colecciones
CREATE TABLE IF NOT EXISTS collections (
    collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_name TEXT NOT NULL UNIQUE,
    card_count INTEGER NOT NULL,
    requires_code INTEGER NOT NULL DEFAULT 0,  -- bool: 0/1
    code_field_name TEXT,                       -- ej "Código", "Set"
    code_header_id INTEGER NOT NULL,
    is_premium INTEGER NOT NULL DEFAULT 0,
    license_key_required TEXT,                  -- hash si es premium, NULL si free
    FOREIGN KEY (code_header_id) REFERENCES codes_headers(code_header_id)
);

-- Cards (catalogo)
CREATE TABLE IF NOT EXISTS cards (
    collection_id INTEGER NOT NULL,
    code_id TEXT NOT NULL,
    card_number INTEGER NOT NULL,
    card_name TEXT NOT NULL,
    PRIMARY KEY (collection_id, code_id, card_number),
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_cards_collection ON cards(collection_id);

-- Inventario del usuario
CREATE TABLE IF NOT EXISTS inventory (
    collection_id INTEGER NOT NULL,
    code_id TEXT NOT NULL,
    card_number INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    image_path TEXT,
    PRIMARY KEY (collection_id, code_id, card_number),
    FOREIGN KEY (collection_id, code_id, card_number)
        REFERENCES cards(collection_id, code_id, card_number)
        ON DELETE CASCADE
);

-- Log de transacciones (alta/baja con timestamp)
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_id INTEGER NOT NULL,
    code_id TEXT NOT NULL,
    card_number INTEGER NOT NULL,
    operation TEXT NOT NULL CHECK (operation IN ('alta', 'baja')),
    quantity INTEGER NOT NULL,
    transaction_date TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id)
);

CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_collection ON transactions(collection_id);

-- Marcar esta migracion como aplicada
INSERT INTO schema_version (version) VALUES (1);
