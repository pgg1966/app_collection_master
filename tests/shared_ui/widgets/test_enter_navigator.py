"""Tests del EnterNavigator."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLineEdit, QSpinBox, QWidget

from collections_app.shared_ui.widgets.enter_navigator import EnterNavigator


@pytest.fixture
def parent_widget(qtbot):
    w = QWidget()
    qtbot.addWidget(w)
    return w


def test_enter_advances_to_next_widget(qtbot, parent_widget):
    a = QLineEdit(parent_widget)
    b = QLineEdit(parent_widget)
    parent_widget.show()
    qtbot.waitExposed(parent_widget)

    nav = EnterNavigator(parent_widget)
    nav.set_chain([a, b])
    nav.install()

    a.setFocus()
    qtbot.keyClick(a, Qt.Key.Key_Return)
    assert b.hasFocus()


def test_enter_on_last_calls_callback(qtbot, parent_widget):
    a = QLineEdit(parent_widget)
    b = QLineEdit(parent_widget)
    parent_widget.show()
    qtbot.waitExposed(parent_widget)

    calls: list[bool] = []
    nav = EnterNavigator(parent_widget)
    nav.set_chain([a, b])
    nav.on_last_enter = lambda: calls.append(True)
    nav.install()

    b.setFocus()
    qtbot.keyClick(b, Qt.Key.Key_Return)
    assert calls == [True]


def test_navigator_with_combobox(qtbot, parent_widget):
    a = QLineEdit(parent_widget)
    combo = QComboBox(parent_widget)
    combo.addItems(["one", "two"])
    spin = QSpinBox(parent_widget)
    parent_widget.show()
    qtbot.waitExposed(parent_widget)

    nav = EnterNavigator(parent_widget)
    nav.set_chain([a, combo, spin])
    nav.install()

    a.setFocus()
    qtbot.keyClick(a, Qt.Key.Key_Return)
    assert combo.hasFocus()
    qtbot.keyClick(combo, Qt.Key.Key_Return)
    assert spin.hasFocus()


def test_navigator_handles_empty_chain(qtbot, parent_widget):
    nav = EnterNavigator(parent_widget)
    nav.set_chain([])
    nav.install()
    # No debe romper aunque no haya widgets en la cadena
    assert nav._installed is True


def test_navigator_uninstall_removes_filters(qtbot, parent_widget):
    a = QLineEdit(parent_widget)
    b = QLineEdit(parent_widget)
    parent_widget.show()
    qtbot.waitExposed(parent_widget)

    nav = EnterNavigator(parent_widget)
    nav.set_chain([a, b])
    nav.install()
    nav.uninstall()

    a.setFocus()
    qtbot.keyClick(a, Qt.Key.Key_Return)
    # Sin filter, Enter no salta a b
    assert not b.hasFocus()


def test_navigator_keypad_enter_also_works(qtbot, parent_widget):
    a = QLineEdit(parent_widget)
    b = QLineEdit(parent_widget)
    parent_widget.show()
    qtbot.waitExposed(parent_widget)

    nav = EnterNavigator(parent_widget)
    nav.set_chain([a, b])
    nav.install()

    a.setFocus()
    qtbot.keyClick(a, Qt.Key.Key_Enter)
    assert b.hasFocus()
