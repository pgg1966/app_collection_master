"""Tests del ExchangeProposalDialog — smoke + flow + manejo de errores."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout

from collections_app.app_context import AppContext
from collections_app.core.models.aggregates.exchange_proposal import (
    ExchangeProposal,
    ProposedExchange,
)
from collections_app.core.models.collection import Collection
from collections_app.services.exchange_errors import InsufficientInventory
from collections_app.views.exchange.proposal_dialog import ExchangeProposalDialog

pytestmark = pytest.mark.gui


def _proposal_with_two_rows() -> ExchangeProposal:
    return ExchangeProposal(
        cards_to_receive=(ProposedExchange("ARG", 2, "Di María", 1, 1),),
        cards_to_give=(ProposedExchange("ARG", 1, "Messi", 1, 2),),
    )


def test_dialog_constructs_with_two_grids_side_by_side(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Layout requerido (ajuste 1 del plan): grids en HBox, no apilados."""
    dlg = ExchangeProposalDialog(
        ctx=ctx_with_demo,
        collection=demo_collection,
        proposal=_proposal_with_two_rows(),
    )
    qtbot.addWidget(dlg)
    # Buscar el HBoxLayout que contiene las dos grillas.
    found_hbox = False
    for child in dlg.findChildren(QHBoxLayout):
        # Un HBox con dos QVBoxLayouts adentro (cada grilla en su columna).
        if child.count() == 2:
            found_hbox = True
            break
    assert found_hbox, "Las dos grillas deben estar en un HBox lado a lado"


def test_dialog_apply_button_disabled_when_nothing_checked(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    dlg = ExchangeProposalDialog(
        ctx=ctx_with_demo,
        collection=demo_collection,
        proposal=_proposal_with_two_rows(),
    )
    qtbot.addWidget(dlg)
    # Por default todas tildadas → botón habilitado.
    assert dlg._apply_btn.isEnabled()
    # Destildar todo en ambas grillas.
    dlg._receive_model.setData(
        dlg._receive_model.index(0, 0),
        Qt.CheckState.Unchecked.value,
        Qt.ItemDataRole.CheckStateRole,
    )
    dlg._give_model.setData(
        dlg._give_model.index(0, 0),
        Qt.CheckState.Unchecked.value,
        Qt.ItemDataRole.CheckStateRole,
    )
    assert not dlg._apply_btn.isEnabled()


def test_summary_label_reflects_checked_quantities(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    dlg = ExchangeProposalDialog(
        ctx=ctx_with_demo,
        collection=demo_collection,
        proposal=_proposal_with_two_rows(),
    )
    qtbot.addWidget(dlg)
    # 1 + 1 cuando todas tildadas.
    assert "1" in dlg._summary_label.text()
    # Destildo el receive → recibo 0.
    dlg._receive_model.setData(
        dlg._receive_model.index(0, 0),
        Qt.CheckState.Unchecked.value,
        Qt.ItemDataRole.CheckStateRole,
    )
    # El label debe haber cambiado.
    assert "Recibís 0" in dlg._summary_label.text()


def test_warnings_banner_hidden_when_empty(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    dlg = ExchangeProposalDialog(
        ctx=ctx_with_demo,
        collection=demo_collection,
        proposal=_proposal_with_two_rows(),
        warnings=(),
    )
    qtbot.addWidget(dlg)
    # No debe haberse construido el botón toggle.
    assert not hasattr(dlg, "_toggle_btn")


def test_warnings_banner_shown_with_warnings(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    dlg = ExchangeProposalDialog(
        ctx=ctx_with_demo,
        collection=demo_collection,
        proposal=_proposal_with_two_rows(),
        warnings=("FRA-99 (Mbappé): no existe en tu colección.",),
    )
    qtbot.addWidget(dlg)
    # Como hay solo 1 warning, no se muestra el botón toggle (cabe en el preview).
    assert not hasattr(dlg, "_toggle_btn")


def test_warnings_toggle_when_more_than_preview(
    qtbot,  # type: ignore[no-untyped-def]
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Más de 5 warnings → aparece el botón toggle."""
    warnings = tuple(f"X-{i}: missing" for i in range(20))
    dlg = ExchangeProposalDialog(
        ctx=ctx_with_demo,
        collection=demo_collection,
        proposal=_proposal_with_two_rows(),
        warnings=warnings,
    )
    qtbot.addWidget(dlg)
    assert hasattr(dlg, "_toggle_btn")
    assert hasattr(dlg, "_extra_container")
    # `isHidden` no depende de que el dialog esté show()-eado.
    assert dlg._extra_container.isHidden() is True
    # Toggle on.
    dlg._toggle_btn.setChecked(True)
    assert dlg._extra_container.isHidden() is False
    # Toggle off.
    dlg._toggle_btn.setChecked(False)
    assert dlg._extra_container.isHidden() is True


def test_apply_calls_service_with_filtered_proposal(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Apply pasa una propuesta filtrada por checkboxes al service."""
    captured: dict[str, ExchangeProposal] = {}
    real_apply = ctx_with_demo.exchange_apply.apply_proposal

    def spy(*, proposal, collection_id):  # type: ignore[no-untyped-def]
        captured["proposal"] = proposal
        return real_apply(proposal=proposal, collection_id=collection_id)

    monkeypatch.setattr(ctx_with_demo.exchange_apply, "apply_proposal", spy)
    # Stub de QMessageBox.question para auto-confirmar.
    from collections_app.views.exchange import proposal_dialog as mod

    monkeypatch.setattr(
        mod.QMessageBox,
        "question",
        lambda *a, **k: mod.QMessageBox.StandardButton.Yes,
    )

    dlg = ExchangeProposalDialog(
        ctx=ctx_with_demo,
        collection=demo_collection,
        proposal=_proposal_with_two_rows(),
    )
    qtbot.addWidget(dlg)
    # Destilar el receive: ya no recibo nada, solo doy.
    dlg._receive_model.setData(
        dlg._receive_model.index(0, 0),
        Qt.CheckState.Unchecked.value,
        Qt.ItemDataRole.CheckStateRole,
    )
    dlg._on_apply()

    assert "proposal" in captured
    assert len(captured["proposal"].cards_to_receive) == 0
    assert len(captured["proposal"].cards_to_give) == 1
    assert dlg.applied_event_id is not None


def test_apply_handles_insufficient_inventory_gracefully(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """InsufficientInventory → QMessageBox.critical, dialog NO se cierra."""

    def boom(*, proposal, collection_id):  # type: ignore[no-untyped-def]
        raise InsufficientInventory("simulated mid-flight mutation")

    monkeypatch.setattr(ctx_with_demo.exchange_apply, "apply_proposal", boom)
    from collections_app.views.exchange import proposal_dialog as mod

    monkeypatch.setattr(
        mod.QMessageBox,
        "question",
        lambda *a, **k: mod.QMessageBox.StandardButton.Yes,
    )
    monkeypatch.setattr(mod.QMessageBox, "critical", lambda *a, **k: None)

    dlg = ExchangeProposalDialog(
        ctx=ctx_with_demo,
        collection=demo_collection,
        proposal=_proposal_with_two_rows(),
    )
    qtbot.addWidget(dlg)
    dlg._on_apply()
    # No se aplicó.
    assert dlg.applied_event_id is None
    # No se aceptó (sigue abierto).
    assert dlg.result() != dlg.DialogCode.Accepted


def test_apply_aborted_on_user_no_does_not_call_service(
    qtbot,  # type: ignore[no-untyped-def]
    monkeypatch: pytest.MonkeyPatch,
    ctx_with_demo: AppContext,
    demo_collection: Collection,
) -> None:
    """Si el user dice "No" en la confirmación, no se llama al service."""
    called = {"n": 0}

    def spy(**kwargs):  # type: ignore[no-untyped-def]
        called["n"] += 1

    monkeypatch.setattr(ctx_with_demo.exchange_apply, "apply_proposal", spy)
    from collections_app.views.exchange import proposal_dialog as mod

    monkeypatch.setattr(
        mod.QMessageBox,
        "question",
        lambda *a, **k: mod.QMessageBox.StandardButton.No,
    )

    dlg = ExchangeProposalDialog(
        ctx=ctx_with_demo,
        collection=demo_collection,
        proposal=_proposal_with_two_rows(),
    )
    qtbot.addWidget(dlg)
    dlg._on_apply()
    assert called["n"] == 0
    assert dlg.applied_event_id is None
