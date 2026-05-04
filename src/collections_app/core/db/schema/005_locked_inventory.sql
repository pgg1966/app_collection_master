-- =========================================================
-- Migration 005 — Bloqueo de inventario para intercambios
-- =========================================================
--
-- Agrega `locked` a `inventory`: cantidad reservada para un
-- intercambio en curso. La cantidad disponible para nueva
-- carga/intercambio es `quantity - locked` (mínimo 0).
--
-- Mientras un dialog de "Ejecutar Intercambio" está abierto,
-- las cards a entregar quedan bloqueadas. Al cancelar/cerrar
-- el dialog, `unlock_all_cards` resetea la columna a 0.
-- Al ejecutar el intercambio se da de baja y luego unlock 0.

PRAGMA foreign_keys = ON;

ALTER TABLE inventory ADD COLUMN locked INTEGER NOT NULL DEFAULT 0;

INSERT INTO schema_version (version) VALUES (5);
