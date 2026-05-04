"""Tests del CardLoaderView.

Reescritos tras rediseño en el cual:
- Se removió el checkbox "Tiene código de prefijo".
- Se removió el DEFAULT_CODE = "NON" hardcodeado.
- requires_code=False → solo Número/Cantidad, búsqueda por find_by_number.
- requires_code=True → Código siempre obligatorio.
- Ambigüedad (>1 match en find_by_number) muestra combo limitado.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox

from collections_app.client.views.card_loader import CardLoaderView
from collections_app.core.models import Card, CodeLine, Collection
from collections_app.core.repositories import (
    CardsRepository,
    CodesLinesRepository,
    CollectionsRepository,
    InventoryRepository,
)
from collections_app.core.services import InventoryService

# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def collection_no_code(memory_db, sample_code_header):
    """Collection con requires_code=False y cards de ejemplo.

    Los códigos del header son `ARG`, `BRA`, `MR`. Hay un número repetido
    (24) en ARG y BRA para tests de ambigüedad.
    """
    hid = sample_code_header.code_header_id
    lines_repo = CodesLinesRepository(memory_db)
    for code, name in [("ARG", "ARGENTINA"), ("BRA", "BRAZIL"), ("MR", "MASTER ROOKIES")]:
        lines_repo.upsert(CodeLine(hid, code, name))

    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Adrenalyne",
            card_count=100,
            requires_code=False,  # ← clave del nuevo diseño
            code_field_name=None,
            code_header_id=hid,
        )
    )
    cards_repo = CardsRepository(memory_db)
    cards_repo.upsert(Card(col.collection_id, "ARG", 24, "LIONEL MESSI"))
    cards_repo.upsert(Card(col.collection_id, "BRA", 24, "VINICIUS"))  # ambiguo con ARG-24
    cards_repo.upsert(Card(col.collection_id, "ARG", 1, "GOLDEN BALLERS"))
    cards_repo.upsert(Card(col.collection_id, "MR", 5, "PAZ"))
    memory_db.commit()
    return col


@pytest.fixture
def collection_with_code(memory_db, sample_code_header):
    """Collection con requires_code=True (modo Stickers Panini)."""
    hid = sample_code_header.code_header_id
    lines_repo = CodesLinesRepository(memory_db)
    for code, name in [("S1", "Set 1"), ("S2", "Set 2")]:
        lines_repo.upsert(CodeLine(hid, code, name))

    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Stickers",
            card_count=20,
            requires_code=True,
            code_field_name="Set",
            code_header_id=hid,
        )
    )
    CardsRepository(memory_db).upsert(Card(col.collection_id, "S1", 1, "Sticker A"))
    CardsRepository(memory_db).upsert(Card(col.collection_id, "S2", 1, "Sticker B"))
    memory_db.commit()
    return col


# ----------------------------------------------------------------------
# Tests de visibilidad y foco
# ----------------------------------------------------------------------


def test_no_checkbox_visible(qtbot, memory_db, collection_no_code):
    """El checkbox de prefijo ya no existe en ningún caso."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    checkboxes = view.findChildren(QCheckBox)
    assert checkboxes == []


def test_no_code_field_when_requires_code_false(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    assert view._code_edit.isVisible() is False
    assert view._code_label.isVisible() is False


def test_code_field_always_visible_when_requires_code_true(qtbot, memory_db, collection_with_code):
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    assert view._code_edit.isVisible() is True
    assert view._code_label.isVisible() is True


def test_focus_on_number_when_requires_code_false(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.wait(50)
    assert view._number_input.hasFocus()


def test_focus_on_code_when_requires_code_true(qtbot, memory_db, collection_with_code):
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.wait(50)
    assert view._code_edit.hasFocus()


# ----------------------------------------------------------------------
# Validación con find_by_number (requires_code=False)
# ----------------------------------------------------------------------


def test_find_by_number_when_requires_code_false(qtbot, memory_db, collection_no_code):
    """Con número único MR-5, autocompleta país/nombre y muestra Nueva."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    assert view._name_input.text() == "PAZ"
    assert "MASTER ROOKIES" in view._country_input.text()
    assert "Nueva" in view._status_label.text()


def test_unknown_number_shows_clear_message(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("9999")
    assert "9999" in view._status_label.text()
    assert "no existe" in view._status_label.text().lower()
    assert view._name_input.text() == ""


def test_ambiguous_number_shows_code_selector(qtbot, memory_db, collection_no_code):
    """Número 24 está en ARG y BRA → debe mostrar el campo y pedir código."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    assert view._has_ambiguity is True
    assert view._code_edit.isVisible() is True
    # El completer solo debe contener los códigos ambiguos (ARG y BRA, no MR)
    assert view._valid_code_ids == {"ARG", "BRA"}
    assert (
        "especificá" in view._status_label.text().lower()
        or "especifica" in view._status_label.text().lower()
    )


def test_choosing_code_after_ambiguity_validates_correctly(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    # Elegir ARG escribiéndolo y disparando Enter
    view._code_edit.setText("ARG")
    view._on_code_return_pressed()
    assert view._name_input.text() == "LIONEL MESSI"
    assert "ARGENTINA" in view._country_input.text()
    assert "Nueva" in view._status_label.text()


# ----------------------------------------------------------------------
# Save: dispatch correcto entre by_number y con código
# ----------------------------------------------------------------------


def test_save_uses_add_card_by_number_when_unambiguous(qtbot, memory_db, collection_no_code):
    """Caso Adrenalyn: número único → save sin pedir código."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    qtbot.keyClick(view._number_input, Qt.Key.Key_Return)
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)

    item = InventoryRepository(memory_db).get(collection_no_code.collection_id, "MR", 5)
    assert item is not None
    assert item.quantity == 1


def test_save_uses_add_card_when_user_specified_code(qtbot, memory_db, collection_no_code):
    """Tras desambiguar, el save usa el código elegido."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    # Ambigüedad: el campo de código aparece. Elegir BRA.
    view._code_edit.setText("BRA")
    view._on_code_return_pressed()
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)

    item_arg = InventoryRepository(memory_db).get(collection_no_code.collection_id, "ARG", 24)
    item_bra = InventoryRepository(memory_db).get(collection_no_code.collection_id, "BRA", 24)
    assert item_arg is None or item_arg.quantity == 0
    assert item_bra is not None
    assert item_bra.quantity == 1


def test_save_alta_increments_inventory_correctly(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    view._qty_input.setText("3")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    item = InventoryRepository(memory_db).get(collection_no_code.collection_id, "MR", 5)
    assert item is not None
    assert item.quantity == 3


def test_save_baja_decrements_inventory_correctly(qtbot, memory_db, collection_no_code):
    InventoryService(memory_db).add_card_by_number(collection_no_code.collection_id, 5, 3)
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._baja_radio.setChecked(True)
    view._number_input.setText("5")
    view._qty_input.setText("2")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    item = InventoryRepository(memory_db).get(collection_no_code.collection_id, "MR", 5)
    assert item is not None
    assert item.quantity == 1


def test_form_resets_after_save_keeping_focus(qtbot, memory_db, collection_no_code):
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    qtbot.wait(50)
    assert view._number_input.text() == ""
    assert view._qty_input.text() == "1"
    assert view._country_input.text() == ""
    assert view._number_input.hasFocus()


# ----------------------------------------------------------------------
# Regresión: bug original (NON-24 hardcodeado)
# ----------------------------------------------------------------------


def test_typing_number_24_finds_messi_in_adrenalyn_like_setup(qtbot, memory_db, collection_no_code):
    """Reproduce el bug: con requires_code=False, tipear '24' debe encontrar
    la card sin importar el código (vía find_by_number, no NON-24)."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("24")
    # No debe decir "NON-24 no existe"; o muestra info (si fuera unívoco)
    # o pide desambiguar (este caso, es ambiguo).
    msg = view._status_label.text().lower()
    assert "non-24" not in msg
    assert "no existe" not in msg or "especificá" in msg


# ----------------------------------------------------------------------
# Autocompletado: QLineEdit + QCompleter (reemplazo del QComboBox)
# ----------------------------------------------------------------------


def test_completer_contains_code_and_name(qtbot, memory_db, collection_with_code):
    """El modelo del completer tiene strings tipo 'S1 - Set 1'."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    model = view._completer.model()
    items = [model.data(model.index(i, 0)) for i in range(model.rowCount())]
    assert "S1 - Set 1" in items
    assert "S2 - Set 2" in items


def test_enter_exact_match_selects_code(qtbot, memory_db, collection_with_code):
    """Texto 'S1' + Enter → _selected_code_id='S1' y foco en número."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._code_edit.setText("S1")
    view._on_code_return_pressed()
    qtbot.wait(50)  # dejar que Qt procese los focus events
    assert view._selected_code_id == "S1"
    assert view._number_input.hasFocus()


def test_enter_case_insensitive(qtbot, memory_db, collection_with_code):
    """Texto en minúsculas 's1' + Enter → matchea 'S1'."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    view._code_edit.setText("s1")
    view._on_code_return_pressed()
    assert view._selected_code_id == "S1"


def test_enter_no_match_does_not_select(qtbot, memory_db, collection_with_code):
    """Texto que no matchea ningún code → _selected_code_id queda en None."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    view._code_edit.setText("ZZZ")
    view._on_code_return_pressed()
    assert view._selected_code_id is None


def test_enter_single_partial_match_auto_selects(qtbot, memory_db, sample_code_header):
    """Solo 'ARG' empieza con 'AR' → tipear 'AR' + Enter selecciona 'ARG'."""
    hid = sample_code_header.code_header_id
    lines_repo = CodesLinesRepository(memory_db)
    for code, name in [("ARG", "ARGENTINA"), ("BRA", "BRAZIL")]:
        lines_repo.upsert(CodeLine(hid, code, name))
    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="Test",
            card_count=10,
            requires_code=True,
            code_field_name="P",
            code_header_id=hid,
        )
    )
    memory_db.commit()
    view = CardLoaderView(memory_db, col)
    qtbot.addWidget(view)
    view.show()
    view._code_edit.setText("AR")  # 'AR' contained only in 'ARG'
    view._on_code_return_pressed()
    assert view._selected_code_id == "ARG"


def test_text_change_after_selection_clears_selection(qtbot, memory_db, collection_with_code):
    """Si el usuario cambia el texto después de seleccionar, _selected_code_id se invalida."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    view._code_edit.setText("S1")
    view._on_code_return_pressed()
    assert view._selected_code_id == "S1"
    # Cambiar texto a algo que no matchea
    view._code_edit.setText("S")  # prefix incompleto: no matchea exactamente
    assert view._selected_code_id is None


def test_on_code_selected_extracts_code_id(qtbot, memory_db, collection_with_code):
    """Llamar _on_code_selected('S1 - Set 1') → extrae 'S1' y setea el text."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._on_code_selected("S1 - Set 1")
    qtbot.wait(50)  # dejar que Qt procese los focus events
    assert view._selected_code_id == "S1"
    assert view._code_edit.text() == "S1"
    assert view._number_input.hasFocus()


def test_on_code_selected_ignores_invalid(qtbot, memory_db, collection_with_code):
    """Si pasamos un string inválido, no se setea selected_code_id."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    view._on_code_selected("FAKE - No existe")
    assert view._selected_code_id is None


def test_add_card_blocked_when_no_code_selected(qtbot, memory_db, collection_with_code):
    """requires_code=True + sin code seleccionado: save bloqueado."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    # Tipear número y cantidad sin haber seleccionado código
    view._number_input.setText("1")
    view._qty_input.setText("1")
    view._save_card()
    # Inventario debe seguir vacío
    item = InventoryRepository(memory_db).get(collection_with_code.collection_id, "S1", 1)
    assert item is None or item.quantity == 0
    # Status debe avisar la falta de código
    assert "código" in view._status_label.text().lower()


def test_completer_uses_contains_match_filter(qtbot, memory_db, collection_with_code):
    """El completer está configurado en MatchContains (no MatchStartsWith)."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    assert view._completer.filterMode() == Qt.MatchFlag.MatchContains
    assert view._completer.caseSensitivity() == Qt.CaseSensitivity.CaseInsensitive


def test_arrow_down_opens_completer_popup(qtbot, memory_db, collection_with_code):
    """Down/Up con popup cerrado: abrir el popup para que se pueda navegar."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._code_edit.setFocus()
    qtbot.wait(50)

    popup = view._completer.popup()
    assert popup is not None
    assert popup.isVisible() is False
    qtbot.keyClick(view._code_edit, Qt.Key.Key_Down)
    # waitUntil es más robusto que wait fijo: poll hasta que el popup
    # se muestre o timeout (focus events son flaky en pytest-qt headless).
    qtbot.waitUntil(lambda: popup.isVisible(), timeout=2000)
    assert popup.isVisible() is True


def test_arrow_down_uses_text_as_prefix_filter(qtbot, memory_db, sample_code_header):
    """Tipear 'AR' + Down filtra el popup a los matches que contienen 'AR'."""
    hid = sample_code_header.code_header_id
    lines_repo = CodesLinesRepository(memory_db)
    for code, name in [("ARG", "ARGENTINA"), ("BRA", "BRAZIL"), ("MAR", "MOROCCO")]:
        lines_repo.upsert(CodeLine(hid, code, name))
    col = CollectionsRepository(memory_db).create(
        Collection(
            collection_id=None,
            collection_name="C",
            card_count=10,
            requires_code=True,
            code_field_name="P",
            code_header_id=hid,
        )
    )
    memory_db.commit()
    view = CardLoaderView(memory_db, col)
    qtbot.addWidget(view)
    view.show()

    view._code_edit.setText("AR")
    qtbot.keyClick(view._code_edit, Qt.Key.Key_Down)
    # Tras complete() con prefix "AR", el modelo de completion solo
    # contiene los matches con "AR" (ARG y MAR, no BRA).
    matches = []
    completion_model = view._completer.completionModel()
    for i in range(completion_model.rowCount()):
        matches.append(completion_model.data(completion_model.index(i, 0)))
    assert any("ARG" in m for m in matches)
    assert any("MAR" in m for m in matches)
    assert not any("BRA - " in m for m in matches)


# ----------------------------------------------------------------------
# Flujo post-carga: mantener SET seleccionado + Enter inmediato → número
# ----------------------------------------------------------------------


def _save_one_card(view, qtbot) -> None:
    """Helper: completa un alta válida (S1, número 1, qty 1)."""
    view._code_edit.setText("S1")
    view._on_code_return_pressed()  # confirma S1, foco va al número
    view._number_input.setText("1")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)


def test_after_load_focus_goes_to_code_field(qtbot, memory_db, collection_with_code):
    """Post-carga (requires_code): foco vuelve al SET con texto seleccionado."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    _save_one_card(view, qtbot)
    qtbot.wait(50)
    assert view._code_edit.hasFocus()
    # selectedText() == text() significa "todo el contenido seleccionado"
    assert view._code_edit.selectedText() == view._code_edit.text() == "S1"


def test_after_load_set_confirmed_flag_is_true(qtbot, memory_db, collection_with_code):
    """Post-carga setea `_set_confirmed=True` para el atajo de Enter."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    _save_one_card(view, qtbot)
    qtbot.wait(50)
    assert view._set_confirmed is True


def test_enter_on_set_without_change_goes_to_number(qtbot, memory_db, collection_with_code):
    """Set confirmado + Enter sin tipear nada → foco al número, set intacto."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    _save_one_card(view, qtbot)
    qtbot.wait(50)
    # Estado pre-Enter: set confirmado, "S1" seleccionado.
    assert view._set_confirmed is True
    # Enter sobre el SET (sin tipear nada extra)
    view._on_code_return_pressed()
    assert view._number_input.hasFocus()
    assert view._selected_code_id == "S1"
    # El flag se consume al saltar
    assert view._set_confirmed is False


def test_typing_in_set_clears_confirmed_flag(qtbot, memory_db, collection_with_code):
    """Input real del usuario en el SET invalida `_set_confirmed`."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    _save_one_card(view, qtbot)
    qtbot.wait(50)
    assert view._set_confirmed is True
    # Tipear (qtbot.keyClicks dispara textEdited a diferencia de setText).
    qtbot.keyClicks(view._code_edit, "X")
    assert view._set_confirmed is False
    # Tampoco quedó código seleccionado (X no matchea ningún code_id).
    assert view._selected_code_id is None


def test_enter_on_set_with_change_validates_new_code(qtbot, memory_db, collection_with_code):
    """Si el usuario cambia el SET a otro válido, Enter selecciona el nuevo."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    _save_one_card(view, qtbot)
    qtbot.wait(50)
    # Reemplazar S1 por S2 con input real (selectAll ya hizo qtbot)
    view._code_edit.clear()
    qtbot.keyClicks(view._code_edit, "S2")
    view._on_code_return_pressed()
    # Debió validar y seleccionar S2 (no haber tomado el atajo de set_confirmed).
    assert view._selected_code_id == "S2"
    assert view._number_input.hasFocus()


def test_highlight_first_completion_sets_row_zero(qtbot, memory_db, collection_with_code):
    """`_highlight_first_completion` resalta el primer ítem visible."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    # Forzar al completer a tener completions disponibles.
    view._completer.setCompletionPrefix("")  # sin filtro: todos los items
    view._highlight_first_completion()
    assert view._completer.currentRow() == 0


# ----------------------------------------------------------------------
# Regresión: el campo de código se LIMPIA en colecciones sin requires_code
# ----------------------------------------------------------------------


def test_no_requires_code_after_load_focuses_number_directly(qtbot, memory_db, collection_no_code):
    """Sin requires_code: post-carga vuelve directo al número (sin SET)."""
    view = CardLoaderView(memory_db, collection_no_code)
    qtbot.addWidget(view)
    view.show()
    view._number_input.setText("5")  # MR-5 está en el catálogo, único
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    qtbot.wait(50)
    assert view._number_input.hasFocus()
    assert view._number_input.text() == ""


# ----------------------------------------------------------------------
# Regresión: el completer inserta solo el code_id, no la etiqueta completa
# ----------------------------------------------------------------------


def test_completer_inserts_only_code_id_not_full_label(qtbot, memory_db, collection_with_code):
    """Activar un ítem del popup deja solo 'S1' en el campo, no 'S1 - Set 1'."""
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()

    view._completer.setCompletionPrefix("")
    completion_model = view._completer.completionModel()
    assert completion_model.rowCount() > 0
    first_idx = completion_model.index(0, 0)
    full_label = completion_model.data(first_idx)
    assert " - " in full_label

    inserted = view._completer.pathFromIndex(first_idx)
    assert " - " not in inserted
    assert inserted.upper() in view._valid_code_ids
    assert inserted == full_label.split(" - ", 1)[0].strip()


# ----------------------------------------------------------------------
# Regresión: tipear sobre SET seleccionado no debe auto-insertar
# el ítem resaltado (era 'FWC' tras tipear 'f' por culpa de
# popup.setCurrentIndex disparando el slot interno del completer).
# ----------------------------------------------------------------------


def test_typing_letter_on_selected_set_does_not_autoinsert_completion(
    qtbot, memory_db, collection_with_code
):
    """Post-carga con SET seleccionado: tipear una letra reemplaza el texto.

    Antes del fix, `_highlight_first_completion` llamaba
    `popup.setCurrentIndex(...)` sin bloquear signals del completer,
    lo que disparaba el auto-insert: tipear 'f' dejaba 'FWC' (o el
    primer match del popup) en el campo en vez de 'f'.
    """
    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    # Cargar una card para llegar al estado post-carga (SET seleccionado).
    view._code_edit.setText("S1")
    view._on_code_return_pressed()
    view._number_input.setText("1")
    qtbot.keyClick(view._qty_input, Qt.Key.Key_Return)
    qtbot.wait(100)
    assert view._code_edit.text() == "S1"
    assert view._code_edit.selectedText() == "S1"
    assert view._set_confirmed is True

    # Tipear 'S' debería reemplazar la selección (texto = 'S'), NO
    # auto-completar a 'S1' o 'S2'.
    qtbot.keyClick(view._code_edit, Qt.Key.Key_S)
    qtbot.wait(100)
    assert view._code_edit.text() == "s", f"Esperado 's', got {view._code_edit.text()!r}"
    assert view._set_confirmed is False


# ----------------------------------------------------------------------
# Tinte de los inputs según el modo Alta/Baja
# ----------------------------------------------------------------------


def test_operation_frame_bg_reflects_alta_mode_by_default(qtbot, memory_db, collection_with_code):
    """Al construir la view (Alta por default), el frame trae el verde."""
    from collections_app.shared_ui.theme import INPUT_BG_ALTA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    assert INPUT_BG_ALTA.lower() in view._operation_frame.styleSheet().lower()


def test_operation_frame_bg_changes_to_baja_when_radio_toggled(
    qtbot, memory_db, collection_with_code
):
    """Al togglear Baja, el frame pasa al tinte rojo."""
    from collections_app.shared_ui.theme import INPUT_BG_ALTA, INPUT_BG_BAJA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()

    view._baja_radio.setChecked(True)
    assert INPUT_BG_BAJA.lower() in view._operation_frame.styleSheet().lower()
    assert INPUT_BG_ALTA.lower() not in view._operation_frame.styleSheet().lower()
    # Y volver a Alta restaura el verde
    view._alta_radio.setChecked(True)
    assert INPUT_BG_ALTA.lower() in view._operation_frame.styleSheet().lower()
    assert INPUT_BG_BAJA.lower() not in view._operation_frame.styleSheet().lower()


# ----------------------------------------------------------------------
# Tinte Alta/Baja también pinta los campos editables (no solo el frame)
# ----------------------------------------------------------------------


def test_alta_applies_green_background_to_fields(qtbot, memory_db, collection_with_code):
    """Modo Alta: número/qty/código tienen fondo verde."""
    from collections_app.shared_ui.theme import INPUT_BG_ALTA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._alta_radio.setChecked(True)
    assert INPUT_BG_ALTA.lower() in view._number_input.styleSheet().lower()
    assert INPUT_BG_ALTA.lower() in view._qty_input.styleSheet().lower()
    assert INPUT_BG_ALTA.lower() in view._code_edit.styleSheet().lower()


def test_baja_applies_pink_background_to_fields(qtbot, memory_db, collection_with_code):
    """Modo Baja: número/qty/código tienen fondo rosa."""
    from collections_app.shared_ui.theme import INPUT_BG_BAJA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    view._baja_radio.setChecked(True)
    assert INPUT_BG_BAJA.lower() in view._number_input.styleSheet().lower()
    assert INPUT_BG_BAJA.lower() in view._qty_input.styleSheet().lower()
    assert INPUT_BG_BAJA.lower() in view._code_edit.styleSheet().lower()


def test_field_color_changes_when_radio_toggles(qtbot, memory_db, collection_with_code):
    """Toggle Alta→Baja→Alta cambia el color del fondo de los campos."""
    from collections_app.shared_ui.theme import INPUT_BG_ALTA, INPUT_BG_BAJA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    # Estado inicial Alta
    assert INPUT_BG_ALTA.lower() in view._number_input.styleSheet().lower()
    # Cambiar a Baja
    view._baja_radio.setChecked(True)
    assert INPUT_BG_BAJA.lower() in view._number_input.styleSheet().lower()
    assert INPUT_BG_ALTA.lower() not in view._number_input.styleSheet().lower()
    # Volver a Alta
    view._alta_radio.setChecked(True)
    assert INPUT_BG_ALTA.lower() in view._number_input.styleSheet().lower()


def test_error_shows_red_border_keeping_bg_color(qtbot, memory_db, collection_with_code):
    """Tras error: borde rojo + bg del modo. Tras revert: solo bg."""
    from collections_app.shared_ui.theme import INPUT_BG_ALTA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    qtbot.waitExposed(view)
    # Modo Alta + disparar error en el código.
    view._alta_radio.setChecked(True)
    view._show_field_error("code")
    style_during = view._code_edit.styleSheet().lower()
    assert "red" in style_during
    assert INPUT_BG_ALTA.lower() in style_during  # bg conservado durante el error
    # Esperar a que expire el QTimer de 1000ms.
    qtbot.wait(1200)
    style_after = view._code_edit.styleSheet().lower()
    assert "red" not in style_after
    assert INPUT_BG_ALTA.lower() in style_after  # vuelve al verde, no a vacío


def test_code_field_gets_color_when_visible(qtbot, memory_db, collection_with_code):
    """Con requires_code=True el campo de código también se tinta."""
    from collections_app.shared_ui.theme import INPUT_BG_BAJA

    view = CardLoaderView(memory_db, collection_with_code)
    qtbot.addWidget(view)
    view.show()
    view._baja_radio.setChecked(True)
    assert view._code_edit.isVisible() is True
    assert INPUT_BG_BAJA.lower() in view._code_edit.styleSheet().lower()
