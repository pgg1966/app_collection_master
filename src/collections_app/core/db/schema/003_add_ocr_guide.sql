-- =========================================================
-- Migration 003 — agrega ocr_guide_filename a collections
-- =========================================================
-- Imagen de instrucciones que el OcrLoaderTab muestra antes
-- de que el usuario cargue fotos (ej. cómo orientar el
-- celular respecto al álbum). Independiente del modelo OCR
-- (`ocr_model_filename`, migración 002).
--
-- - NULL = sin imagen de guía configurada (default).
-- - Cuando el admin configura la imagen, se copia a
--   `%APPDATA%/Collections/images/` con nombre canónico
--   `ocr_guide_<collection_id>.<ext>` y se persiste el
--   filename acá; el path completo se reconstruye con
--   `get_images_dir()`.
--
-- Migración inmutable (CLAUDE.md sec 2.7).

ALTER TABLE collections
    ADD COLUMN ocr_guide_filename TEXT;

INSERT INTO schema_version (version) VALUES (3);
