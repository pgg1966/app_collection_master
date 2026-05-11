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

# Paleta del Pulido Nivel 1 (Prompt 6). Solo se agregan bordes +
# negrita + un tinte sutil de selección — la paleta principal de la
# app no cambia. El objetivo es que los controles interactivos
# (botones, tabs, items seleccionados) se distingan claramente del
# fondo sin rediseñar nada.
COLOR_BORDER = "#404040"  # bordes (gris oscuro)
COLOR_BTN_BG = "#ECECEC"  # fondo de botones (gris claro)
COLOR_BTN_HOVER = "#D8D8D8"
COLOR_BTN_PRESSED = "#C5C5C5"
COLOR_TAB_SELECTED_BG = "#D8D8D8"
COLOR_LIST_SELECTED_BG = "#B3D9FF"  # azul claro para fila seleccionada

# Tintes pastel para los inputs según el modo Alta/Baja en CardLoader.
# Sirven como recordatorio visual constante (el usuario carga muchas
# cards seguidas y el radio button solo es una pista chica). Texto
# negro mantiene legibilidad total sobre ambos.
INPUT_BG_ALTA = "#D5F5E3"  # verde menta suave — modo Alta activo
INPUT_BG_BAJA = "#FADBD8"  # rosa salmón suave — modo Baja activo


# Stylesheet global: aplicado vía `app.setStyleSheet(...)` en
# `apply_app_style`. Acota selectors a los controles interactivos
# (QPushButton, QTabBar, QListWidget, QGroupBox) para no chocar con
# los `setStyleSheet` locales del card_loader (QLineEdit, QLabel,
# QFrame de operación).
_GLOBAL_QSS = f"""
QPushButton {{
    border: 1px solid {COLOR_BORDER};
    background: {COLOR_BTN_BG};
    font-weight: bold;
    padding: 4px 12px;
}}
QPushButton:hover {{
    background: {COLOR_BTN_HOVER};
}}
QPushButton:pressed {{
    background: {COLOR_BTN_PRESSED};
}}
QPushButton:disabled {{
    color: #888888;
    background: #F0F0F0;
}}

QTabBar::tab {{
    border: 1px solid {COLOR_BORDER};
    background: {COLOR_BTN_BG};
    padding: 6px 12px;
    font-weight: bold;
}}
QTabBar::tab:selected {{
    background: {COLOR_TAB_SELECTED_BG};
}}

QListWidget::item:selected {{
    background: {COLOR_LIST_SELECTED_BG};
    color: black;
    font-weight: bold;
}}

QGroupBox {{
    font-weight: bold;
    border: 1px solid {COLOR_BORDER};
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 8px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}}
"""


def apply_app_style(app: QApplication) -> None:
    """Aplica el stylesheet global del Pulido Nivel 1.

    Cubre los controles interactivos (botones, tabs, lista del sidebar,
    group boxes). Los estilos locales del card_loader (QLineEdit con
    tinte alta/baja, frame de operación, etc.) NO se ven afectados —
    los selectors del global no apuntan a esos widgets.
    """
    app.setStyleSheet(_GLOBAL_QSS)
