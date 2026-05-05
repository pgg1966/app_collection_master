"""Tests CRUD + queries de CardImagesRepository."""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.card_image import CardImage
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.card_images_repo import CardImagesRepository
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository


@pytest.fixture
def repo(db_conn: sqlite3.Connection) -> CardImagesRepository:
    return CardImagesRepository(db_conn)


@pytest.fixture
def cards_repo(db_conn: sqlite3.Connection) -> CardsRepository:
    return CardsRepository(db_conn)


@pytest.fixture
def collection_id(db_conn: sqlite3.Connection) -> int:
    h = CodeHeadersRepository(db_conn).create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="C",
            card_count=10,
            requires_code=False,
            code_field_name=None,
            code_header_id=h.code_header_id,
        )
    )
    assert c.collection_id is not None
    return c.collection_id


def _make_card(cards_repo: CardsRepository, collection_id: int, n: int) -> int:
    saved = cards_repo.create(
        Card(
            card_id=None,
            collection_id=collection_id,
            code_id="X",
            card_number=n,
            card_name=f"X-{n}",
        )
    )
    assert saved.card_id is not None
    return saved.card_id


def test_get_by_card_id_returns_none_when_no_image(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    assert repo.get_by_card_id(card_id) is None


def test_upsert_inserts_new(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    saved = repo.upsert(
        CardImage(
            card_image_id=None,
            card_id=card_id,
            found_photo=True,
            image_source="wikipedia",
            image_path="/tmp/a.png",
            generated_at="2026-05-05",
        )
    )
    assert saved.card_image_id is not None
    fetched = repo.get_by_card_id(card_id)
    assert fetched is not None
    assert fetched.image_source == "wikipedia"
    assert fetched.image_path == "/tmp/a.png"
    assert fetched.found_photo is True


def test_upsert_updates_existing_by_card_id(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(
        CardImage(
            card_image_id=None,
            card_id=card_id,
            found_photo=False,
            image_source="placeholder",
        )
    )
    repo.upsert(
        CardImage(
            card_image_id=None,
            card_id=card_id,
            found_photo=True,
            image_source="wikipedia",
            image_path="/tmp/new.png",
        )
    )
    fetched = repo.get_by_card_id(card_id)
    assert fetched is not None
    assert fetched.found_photo is True
    assert fetched.image_source == "wikipedia"
    assert fetched.image_path == "/tmp/new.png"


def test_upsert_violates_fk_when_card_not_exists(
    repo: CardImagesRepository,
) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        repo.upsert(CardImage(card_image_id=None, card_id=999, found_photo=False))


def test_delete_by_card_id_returns_true_when_existed(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(CardImage(card_image_id=None, card_id=card_id, found_photo=False))
    assert repo.delete_by_card_id(card_id) is True
    assert repo.get_by_card_id(card_id) is None


def test_delete_by_card_id_returns_false_when_missing(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    card_id = _make_card(cards_repo, collection_id, 1)
    assert repo.delete_by_card_id(card_id) is False


def test_list_by_collection_filters_correctly(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
    db_conn: sqlite3.Connection,
) -> None:
    other_h = CodeHeadersRepository(db_conn).create(
        CodeHeader(code_header_id=None, code_header_name="OH")
    )
    assert other_h.code_header_id is not None
    other_c = CollectionsRepository(db_conn).create(
        Collection(
            collection_id=None,
            collection_name="OC",
            card_count=1,
            requires_code=False,
            code_field_name=None,
            code_header_id=other_h.code_header_id,
        )
    )
    assert other_c.collection_id is not None
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, other_c.collection_id, 1)
    repo.upsert(CardImage(card_image_id=None, card_id=a, found_photo=True))
    repo.upsert(CardImage(card_image_id=None, card_id=b, found_photo=True))
    items = repo.list_by_collection(collection_id)
    assert len(items) == 1
    assert items[0].card_id == a


def test_get_pending_excludes_cards_with_images(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.upsert(CardImage(card_image_id=None, card_id=a, found_photo=True))
    pending = repo.get_pending(collection_id)
    pending_ids = {c.card_id for c in pending}
    assert b in pending_ids
    assert a not in pending_ids


def test_get_pending_returns_card_dataclasses(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    _make_card(cards_repo, collection_id, 1)
    pending = repo.get_pending(collection_id)
    assert all(isinstance(c, Card) for c in pending)


def test_get_placeholders_only_found_photo_false(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    repo.upsert(CardImage(card_image_id=None, card_id=a, found_photo=True))
    repo.upsert(CardImage(card_image_id=None, card_id=b, found_photo=False))
    placeholders = repo.get_placeholders(collection_id)
    placeholder_card_ids = {p.card_id for p in placeholders}
    assert b in placeholder_card_ids
    assert a not in placeholder_card_ids


def test_count_with_photo_only_found_true(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    c = _make_card(cards_repo, collection_id, 3)
    repo.upsert(CardImage(card_image_id=None, card_id=a, found_photo=True))
    repo.upsert(CardImage(card_image_id=None, card_id=b, found_photo=True))
    repo.upsert(CardImage(card_image_id=None, card_id=c, found_photo=False))
    assert repo.count_with_photo(collection_id) == 2


def test_count_total_generated_includes_placeholders(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    a = _make_card(cards_repo, collection_id, 1)
    b = _make_card(cards_repo, collection_id, 2)
    c = _make_card(cards_repo, collection_id, 3)
    repo.upsert(CardImage(card_image_id=None, card_id=a, found_photo=True))
    repo.upsert(CardImage(card_image_id=None, card_id=b, found_photo=False))
    _ = c  # card sin imagen, no cuenta
    assert repo.count_total_generated(collection_id) == 2


def test_count_zero_when_no_images(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    _make_card(cards_repo, collection_id, 1)
    assert repo.count_with_photo(collection_id) == 0
    assert repo.count_total_generated(collection_id) == 0


def test_card_delete_cascades_to_card_images(
    repo: CardImagesRepository,
    cards_repo: CardsRepository,
    collection_id: int,
) -> None:
    """Borrar la card debe borrar la entry en card_images (CASCADE)."""
    card_id = _make_card(cards_repo, collection_id, 1)
    repo.upsert(CardImage(card_image_id=None, card_id=card_id, found_photo=True))
    cards_repo.delete_by_id(card_id)
    assert repo.get_by_card_id(card_id) is None
