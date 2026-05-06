"""Fixtures compartidas para los tests de views/collections/.

Cada fixture devuelve un AppContext seedeado contra `:memory:` con un
escenario realista para los tests de UI. Marca `gui` se aplica a los
módulos que importan QWidgets, no acá.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from collections_app.app_context import AppContext, create_app_context
from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.code_line import CodeLine
from collections_app.core.models.collection import Collection


@pytest.fixture(autouse=True)
def _qapp() -> Iterator[QApplication | None]:
    """QApplication único por proceso para todos los tests de este package."""
    app = QApplication.instance() or QApplication([])
    yield app  # type: ignore[misc]


@pytest.fixture
def ctx_with_demo() -> Iterator[AppContext]:
    """AppContext con header + 2 codes + 1 colección + 4 cards."""
    ctx = create_app_context(":memory:")
    try:
        h = ctx.code_headers.create(CodeHeader(code_header_id=None, code_header_name="World"))
        assert h.code_header_id is not None
        ctx.code_lines.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=h.code_header_id,
                code_id="ARG",
                code_name="Argentina",
                code_order=1,
            )
        )
        ctx.code_lines.upsert(
            CodeLine(
                code_line_id=None,
                code_header_id=h.code_header_id,
                code_id="BRA",
                code_name="Brasil",
                code_order=2,
            )
        )
        coll = ctx.collections.create(
            Collection(
                collection_id=None,
                collection_name="WC",
                card_count=4,
                requires_code=True,
                code_field_name="País",
                code_header_id=h.code_header_id,
            )
        )
        assert coll.collection_id is not None
        for code, num, name in [
            ("ARG", 1, "Messi"),
            ("ARG", 2, "Di María"),
            ("BRA", 1, "Vinicius"),
            ("BRA", 2, "Rodrygo"),
        ]:
            ctx.cards.create(
                Card(
                    card_id=None,
                    collection_id=coll.collection_id,
                    code_id=code,
                    card_number=num,
                    card_name=name,
                )
            )
        ctx.conn.commit()
        yield ctx
    finally:
        ctx.close()


@pytest.fixture
def demo_collection(ctx_with_demo: AppContext) -> Collection:
    items = ctx_with_demo.collections.list_all()
    assert len(items) == 1
    return items[0]
