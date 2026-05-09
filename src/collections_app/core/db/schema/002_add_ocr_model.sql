-- =========================================================
-- Migration 002 — agrega ocr_model_filename a collections
-- =========================================================
-- Soporte para reconocimiento óptico de cards desde fotos
-- (Sesión 5d). Cada colección puede tener su propio modelo
-- YOLO entrenado para detectar los códigos de sus cards.
--
-- - NULL = OCR no configurado para esta colección.
-- - Cuando el admin configura el modelo, se guarda solo el
--   nombre de archivo (ej: "ocr_1.pt"). El path completo se
--   reconstruye con `get_models_dir()`.
--
-- Migración inmutable (CLAUDE.md sec 2.7).

ALTER TABLE collections
    ADD COLUMN ocr_model_filename TEXT;

-- Marcar esta migración como aplicada. Mantiene historial: cada
-- versión inserta su propia fila (NO se hace UPDATE — patrón
-- definido en la 001).
INSERT INTO schema_version (version) VALUES (2);
