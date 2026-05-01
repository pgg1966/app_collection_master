"""Tests del CardImagesRepository (migración 003)."""

from collections_app.core.models import CardImage
from collections_app.core.repositories import CardImagesRepository


def _img(
    cid: int,
    code: str = "ARG",
    num: int = 1,
    found: bool = True,
    source: str | None = "wikipedia",
    path: str | None = "/tmp/x.png",
    when: str | None = "2026-01-01 12:00:00",
) -> CardImage:
    return CardImage(
        collection_id=cid,
        code_id=code,
        card_number=num,
        found_photo=found,
        image_source=source,
        image_path=path,
        generated_at=when,
    )


def test_upsert_creates_record(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    img = _img(cid, "ARG", 1, found=True, source="wikipedia")
    repo.upsert(img)
    fetched = repo.get(cid, "ARG", 1)
    assert fetched == img


def test_upsert_updates_existing(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1, found=False, source="placeholder"))
    repo.upsert(_img(cid, "ARG", 1, found=True, source="google", path="/tmp/new.png"))
    fetched = repo.get(cid, "ARG", 1)
    assert fetched is not None
    assert fetched.found_photo is True
    assert fetched.image_source == "google"
    assert fetched.image_path == "/tmp/new.png"


def test_get_missing_returns_none(memory_db, sample_collection):
    repo = CardImagesRepository(memory_db)
    assert repo.get(sample_collection.collection_id, "ZZZ", 999) is None


def test_list_by_collection(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1))
    repo.upsert(_img(cid, "BRA", 1, source="duckduckgo"))
    rows = repo.list_by_collection(cid)
    assert len(rows) == 2
    assert {r.code_id for r in rows} == {"ARG", "BRA"}


def test_get_pending_returns_cards_without_image(memory_db, sample_cards, sample_collection):
    """Cards en `cards` que NO están en `card_images`."""
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1))
    repo.upsert(_img(cid, "BRA", 1))
    pending = repo.get_pending(cid)
    pending_keys = {(p.code_id, p.card_number) for p in pending}
    # sample_cards tiene 5 cards: ARG-1, ARG-2, BRA-1, BRA-2, FRA-1.
    # Procesamos ARG-1 y BRA-1 → quedan 3 pendientes.
    assert pending_keys == {("ARG", 2), ("BRA", 2), ("FRA", 1)}


def test_get_placeholders_returns_found_photo_false(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1, found=True, source="wikipedia"))
    repo.upsert(_img(cid, "ARG", 2, found=False, source="placeholder"))
    repo.upsert(_img(cid, "BRA", 1, found=False, source="placeholder"))
    placeholders = repo.get_placeholders(cid)
    keys = {(p.code_id, p.card_number) for p in placeholders}
    assert keys == {("ARG", 2), ("BRA", 1)}


def test_get_found_count(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1, found=True))
    repo.upsert(_img(cid, "ARG", 2, found=True))
    repo.upsert(_img(cid, "BRA", 1, found=False))
    assert repo.get_found_count(cid) == 2


def test_get_total_generated(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1, found=True))
    repo.upsert(_img(cid, "ARG", 2, found=False))
    assert repo.get_total_generated(cid) == 2


def test_delete_removes_record(memory_db, sample_cards, sample_collection):
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1))
    repo.delete(cid, "ARG", 1)
    assert repo.get(cid, "ARG", 1) is None


def test_cascade_delete_when_card_deleted(memory_db, sample_cards, sample_collection):
    """FK ON DELETE CASCADE: si se borra la card, su entry de card_images desaparece."""
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1))
    memory_db.execute(
        "DELETE FROM cards WHERE collection_id = ? AND code_id = ? AND card_number = ?",
        (cid, "ARG", 1),
    )
    memory_db.commit()
    assert repo.get(cid, "ARG", 1) is None


def test_pending_excludes_cards_with_existing_image(memory_db, sample_cards, sample_collection):
    """Si TODAS las cards tienen image, get_pending devuelve lista vacía."""
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    for code, num in [("ARG", 1), ("ARG", 2), ("BRA", 1), ("BRA", 2), ("FRA", 1)]:
        repo.upsert(_img(cid, code, num))
    assert repo.get_pending(cid) == []


def test_collection_isolation(memory_db, sample_cards, sample_collection):
    """Los queries filtran por collection_id."""
    repo = CardImagesRepository(memory_db)
    cid = sample_collection.collection_id
    repo.upsert(_img(cid, "ARG", 1))
    # Otra collection_id no debería encontrar nada
    other_cid = cid + 999
    assert repo.list_by_collection(other_cid) == []
    assert repo.get_found_count(other_cid) == 0
    assert repo.get_total_generated(other_cid) == 0
