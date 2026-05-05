"""Constantes y helpers visuales reutilizables."""

from PySide6.QtWidgets import QApplication


class Spacing:
    """Constantes de espaciado en píxeles."""

    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24


class FontSize:
    """Tamaños de fuente en puntos."""

    SM = 11
    MD = 13
    LG = 16
    XL = 20


class StatusColor:
    """Colores semánticos sutiles para mensajes (no agresivos)."""

    SUCCESS = "#3B6D11"  # verde tenue (alta exitosa, "Nueva")
    INFO = "#1F4E79"  # azul tenue (info general)
    REPEATED = "#993C1D"  # coral tenue (card repetida en inventario)
    WARNING = "#854F0B"  # ámbar tenue (validación, input inválido)
    ERROR = "#A32D2D"  # rojo tenue (error de save, baja sin stock)


# Colores estructurales (header del ABM, fondos, etc.)
HEADER_BG = "#2B2B2B"
HEADER_FG = "#FFFFFF"
READONLY_BG = "#F0F0F0"

# Tintes pastel para los inputs según el modo Alta/Baja en CardLoader.
# Sirven como recordatorio visual constante (el usuario carga muchas
# cards seguidas y el radio button solo es una pista chica). Texto
# negro mantiene legibilidad total sobre ambos.
INPUT_BG_ALTA = "#D5F5E3"  # verde menta suave — modo Alta activo
INPUT_BG_BAJA = "#FADBD8"  # rosa salmón suave — modo Baja activo


def apply_app_style(app: QApplication) -> None:
    """Aplica el estilo de la app.

    Por ahora respeta el estilo nativo del SO. Si en el futuro se quiere
    forzar Fusion para uniformidad cross-platform: `app.setStyle("Fusion")`.
    """
    # Default: estilo nativo de Qt en cada plataforma.
    _ = app  # Placeholder para evitar warnings de variable no usada.
