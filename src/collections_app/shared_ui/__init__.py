"""Capa de UI compartida entre admin y client."""

from collections_app.shared_ui.dialogs.settings_dialog import SettingsDialog
from collections_app.shared_ui.main_window_base import MainWindowBase
from collections_app.shared_ui.theme import (
    FontSize,
    Spacing,
    StatusColor,
    apply_app_style,
)
from collections_app.shared_ui.widgets.abm_widget import (
    AbmConfig,
    AbmWidget,
    FieldDef,
    FieldType,
)
from collections_app.shared_ui.widgets.enter_navigator import EnterNavigator

__all__ = [
    "AbmConfig",
    "AbmWidget",
    "EnterNavigator",
    "FieldDef",
    "FieldType",
    "FontSize",
    "MainWindowBase",
    "SettingsDialog",
    "Spacing",
    "StatusColor",
    "apply_app_style",
]
