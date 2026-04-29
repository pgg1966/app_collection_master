-- =========================================================
-- Migration 002 — Agregar code_order a codes_lines
-- =========================================================

ALTER TABLE codes_lines ADD COLUMN code_order INTEGER NOT NULL DEFAULT 0;

-- Para registros existentes, asignar orden por code_id alfabético
-- (mantiene compatibilidad: si nadie lo configuró, ordena alfabéticamente)
UPDATE codes_lines
SET code_order = (
    SELECT COUNT(*) FROM codes_lines AS cl2
    WHERE cl2.code_header_id = codes_lines.code_header_id
      AND cl2.code_id <= codes_lines.code_id
);

-- Index para queries ordenadas
CREATE INDEX IF NOT EXISTS idx_codes_lines_order
    ON codes_lines(code_header_id, code_order, code_id);

INSERT INTO schema_version (version) VALUES (2);
