"""Modelo AppSetting: par clave/valor de configuración persistido en `app_settings`.

Existe como dataclass aunque la tabla solo tenga 2 columnas porque CLAUDE.md
sec 2.3 prohíbe que un repo retorne `str | None` crudo. El casteo a tipos
derivados (`int`, `bool`) vive acá para que el caller pueda elegir entre el
string original y un tipo parseado sin que el repo sepa nada del contenido.
"""

from __future__ import annotations

from dataclasses import dataclass

_TRUTHY = frozenset({"1", "true", "yes", "on"})
_FALSY = frozenset({"0", "false", "no", "off"})


@dataclass(slots=True)
class AppSetting:
    """Setting clave/valor.

    Attributes:
        key: clave única.
        value: valor crudo como string, o None.
    """

    key: str
    value: str | None

    def as_int(self: AppSetting) -> int | None:
        """Parsea `value` como int. None si `value` es None o no es un entero válido."""
        if self.value is None:
            return None
        try:
            return int(self.value)
        except ValueError:
            return None

    def as_bool(self: AppSetting) -> bool | None:
        """Parsea `value` como bool. None si `value` es None o no reconocible.

        Acepta como verdaderos: '1', 'true', 'yes', 'on' (case/whitespace-insensitive).
        Acepta como falsos:    '0', 'false', 'no', 'off' (idem).
        Cualquier otra cosa retorna None — el caller decide el default.
        """
        if self.value is None:
            return None
        normalized = self.value.strip().lower()
        if normalized in _TRUTHY:
            return True
        if normalized in _FALSY:
            return False
        return None
