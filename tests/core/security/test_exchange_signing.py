"""Tests de `exchange_signing` (HMAC-SHA256 sobre payload)."""

from __future__ import annotations

from collections_app.core.security.exchange_signing import (
    compute_signature,
    verify_signature,
)


def test_signature_is_deterministic() -> None:
    """Mismo payload → misma firma (no depende de orden de inserción)."""
    payload_a = {
        "format": "collections_app_exchange",
        "format_version": 1,
        "missing": [{"code_id": "ARG", "card_number": 1, "needed_quantity": 1}],
    }
    # Mismo contenido, distinto orden de inserción.
    payload_b = {
        "missing": [{"needed_quantity": 1, "card_number": 1, "code_id": "ARG"}],
        "format_version": 1,
        "format": "collections_app_exchange",
    }
    assert compute_signature(payload_a) == compute_signature(payload_b)


def test_signature_is_64_hex_chars() -> None:
    """HMAC-SHA256 hex digest tiene 64 caracteres lowercase."""
    sig = compute_signature({"a": 1})
    assert len(sig) == 64
    assert all(c in "0123456789abcdef" for c in sig)


def test_altered_payload_changes_signature() -> None:
    """Cualquier cambio en el payload cambia el digest."""
    base = {"format_version": 1, "missing": []}
    sig_base = compute_signature(base)
    sig_altered = compute_signature({"format_version": 2, "missing": []})
    assert sig_base != sig_altered


def test_added_field_changes_signature() -> None:
    """Agregar un campo cambia el digest."""
    sig_a = compute_signature({"format_version": 1})
    sig_b = compute_signature({"format_version": 1, "extra": "x"})
    assert sig_a != sig_b


def test_unicode_content_handled_correctly() -> None:
    """Acentos en strings no rompen la firma."""
    payload = {"card_name": "Mbappé", "code_id": "FRA"}
    sig = compute_signature(payload)
    assert verify_signature(payload, sig) is True


def test_verify_signature_accepts_correct_signature() -> None:
    payload = {"format": "collections_app_exchange", "format_version": 1}
    sig = compute_signature(payload)
    assert verify_signature(payload, sig) is True


def test_verify_signature_rejects_tampered_signature() -> None:
    payload = {"format": "collections_app_exchange", "format_version": 1}
    sig = compute_signature(payload)
    # Flip un caracter del hex.
    tampered = ("0" if sig[0] != "0" else "1") + sig[1:]
    assert verify_signature(payload, tampered) is False


def test_verify_signature_rejects_tampered_payload() -> None:
    payload = {"format_version": 1, "missing": []}
    sig = compute_signature(payload)
    altered = {"format_version": 1, "missing": [{"code_id": "X"}]}
    assert verify_signature(altered, sig) is False


def test_verify_signature_rejects_empty_signature() -> None:
    payload = {"format_version": 1}
    assert verify_signature(payload, "") is False


def test_nested_dict_order_doesnt_affect_signature() -> None:
    """Sub-dicts también se ordenan canónicamente."""
    payload_a = {"collection": {"name": "Mundial 2026", "card_count": 670}}
    payload_b = {"collection": {"card_count": 670, "name": "Mundial 2026"}}
    assert compute_signature(payload_a) == compute_signature(payload_b)
