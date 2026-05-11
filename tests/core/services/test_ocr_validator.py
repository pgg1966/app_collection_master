"""Tests del módulo `ocr_validator`.

Cubre los casos del `validator.py` original del usuario + casos
específicos de la implementación DB-driven.
"""

from __future__ import annotations

import sqlite3

import pytest

from collections_app.core.models.card import Card
from collections_app.core.models.code_header import CodeHeader
from collections_app.core.models.collection import Collection
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.code_headers_repo import CodeHeadersRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.services.ocr_validator import (
    CollectionValidator,
    _corregir_a_numero,
    _todas_las_posiciones,
    build_validator,
)

# ---------------------------------------------------------------------
# Validador construido a mano (sin DB) — tests del comportamiento puro
# ---------------------------------------------------------------------


def _make_validator(
    codes: list[str] | None = None,
    *,
    max_by_code: dict[str, int] | None = None,
    default_max: int = 20,
) -> CollectionValidator:
    """Builder de CollectionValidator para tests sin DB."""
    if codes is None:
        codes = [
            "PNN",
            "FWC",
            "MEX",
            "RSA",
            "KOR",
            "CZE",
            "CAN",
            "BIH",
            "QAT",
            "BRA",
            "MAR",
            "HAI",
            "SCO",
            "USA",
            "PAR",
            "AUS",
            "TUR",
            "GER",
            "CIV",
            "ECU",
            "NED",
            "JPN",
            "SWE",
            "TUN",
            "BEL",
            "EGY",
            "IRN",
            "ESP",
            "KSA",
            "URU",
            "FRA",
            "SEN",
            "IRQ",
            "NOR",
            "ARG",
            "ALG",
            "AUT",
            "JOR",
            "POR",
            "COL",
            "ENG",
            "CRO",
            "GHA",
            "PAN",
            "IRO",
        ]
    return CollectionValidator(
        valid_codes=frozenset(codes),
        max_number_by_code=(max_by_code or {"PNN": 1, "FWC": 19}),
        default_max=default_max,
    )


# Casos directos del validator.py original.
@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("KOR6", "KOR 6"),
        ("KORG", "KOR 6"),
        ("CZE5", "CZE 5"),
        ("CZES", "CZE 5"),
        ("TUR20", "TUR 20"),
        ("TUR2O", "TUR 20"),
        ("IRO20", "IRO 20"),
        ("URU19", "URU 19"),
        ("1RO6", "IRO 6"),
        ("FIFAWORLDCUP2026KOR6", "KOR 6"),
    ],
    ids=[
        "exact-KOR6",
        "G_to_6",
        "exact-CZE5",
        "S_to_5",
        "exact-TUR20",
        "O_to_0",
        "exact-IRO20",
        "exact-URU19",
        "1_to_I",
        "noise-around",
    ],
)
def test_validar_codigo_casos_canonicos(texto: str, esperado: str) -> None:
    v = _make_validator()
    assert v.validar_codigo(texto) == esperado


def test_validar_codigo_pnn_solo_devuelve_none() -> None:
    """PNN sin número no parsea (caso del original)."""
    v = _make_validator()
    assert v.validar_codigo("PNN") is None


def test_validar_codigo_codigo_inexistente_devuelve_none() -> None:
    v = _make_validator()
    assert v.validar_codigo("XYZ5") is None


def test_validar_codigo_pnn_con_numero_dentro_del_max() -> None:
    """PNN tiene max 1 — el número 1 debe aceptarse."""
    v = _make_validator()
    assert v.validar_codigo("PNN1") == "PNN 1"


def test_validar_codigo_pnn_numero_excede_max_devuelve_none() -> None:
    """PNN solo va hasta 1; el 5 no debe aceptarse."""
    v = _make_validator()
    assert v.validar_codigo("PNN5") is None


def test_validar_codigo_greedy_fallback_to_single_digit() -> None:
    """Si los 2 dígitos exceden el max, el validator prueba con 1 dígito.

    Comportamiento del validator.py original: para "FWC20" con FWC max=19,
    "20" excede pero "2" entra → devuelve "FWC 2". El caller (UI) decide
    qué hacer con ese matching parcial.
    """
    v = _make_validator()
    assert v.validar_codigo("FWC20") == "FWC 2"


def test_validar_codigo_excedido_en_ambos_largos_devuelve_none() -> None:
    """Si ni los 2 ni 1 dígitos caen dentro del max, no hay candidato."""
    # PNN max=1; "9" como un dígito tampoco entra (1 < 9).
    v = _make_validator()
    assert v.validar_codigo("PNN9") is None


def test_validar_codigo_fwc_numero_dentro_del_max() -> None:
    v = _make_validator()
    assert v.validar_codigo("FWC19") == "FWC 19"


def test_validar_codigo_default_max_respeta_codigo_sin_entry() -> None:
    """Si un código NO está en max_number_by_code, usa default_max."""
    v = _make_validator(max_by_code={}, default_max=5)
    # KOR no está en max_by_code → cap a default_max=5.
    assert v.validar_codigo("KOR3") == "KOR 3"
    assert v.validar_codigo("KOR6") is None


def test_validar_codigo_texto_vacio_devuelve_none() -> None:
    v = _make_validator()
    assert v.validar_codigo("") is None


def test_validar_codigo_texto_none_devuelve_none() -> None:
    v = _make_validator()
    assert v.validar_codigo(None) is None


def test_validar_codigo_solo_simbolos_devuelve_none() -> None:
    v = _make_validator()
    assert v.validar_codigo("@#$%") is None


def test_validar_codigo_score_prefiere_mas_digitos_puros() -> None:
    """Entre dos códigos posibles, gana el que requiere menos correcciones."""
    # "TUR20" matchea TUR + 20 (sin correcciones, score 20).
    # "TUR2O" matchea TUR + 2 (1 char digit puro, score 10) Y
    # TUR + 20 (con 1 corrección O→0, score 19). Gana el segundo.
    v = _make_validator()
    assert v.validar_codigo("TUR2O") == "TUR 20"


# ---------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------


def test_todas_las_posiciones_finds_overlapping_matches() -> None:
    """`_todas_las_posiciones` arranca desde idx+1, encuentra overlaps."""
    assert list(_todas_las_posiciones("AAAA", "AA")) == [0, 1, 2]


def test_todas_las_posiciones_no_match_returns_nothing() -> None:
    assert list(_todas_las_posiciones("XYZ", "AA")) == []


def test_corregir_a_numero_solo_digitos() -> None:
    result, corr = _corregir_a_numero("20")
    assert (result, corr) == ("20", 0)


def test_corregir_a_numero_con_correcciones() -> None:
    result, corr = _corregir_a_numero("2O")
    assert (result, corr) == ("20", 1)


def test_corregir_a_numero_corta_al_encontrar_no_corregible() -> None:
    result, corr = _corregir_a_numero("2X")
    assert (result, corr) == ("2", 0)


# ---------------------------------------------------------------------
# build_validator — lee desde la DB
# ---------------------------------------------------------------------


def _seed_collection_with_codes(
    db_conn: sqlite3.Connection,
    *,
    codes_and_max: list[tuple[str, int]],
) -> int:
    """Crea una colección con cards para los códigos y máximos dados."""
    headers = CodeHeadersRepository(db_conn)
    collections = CollectionsRepository(db_conn)
    cards = CardsRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    coll = collections.create(
        Collection(
            collection_id=None,
            collection_name="WC",
            card_count=sum(m for _, m in codes_and_max),
            requires_code=True,
            code_field_name="País",
            code_header_id=h.code_header_id,
        )
    )
    assert coll.collection_id is not None
    for code, max_num in codes_and_max:
        for n in range(1, max_num + 1):
            cards.create(
                Card(
                    card_id=None,
                    collection_id=coll.collection_id,
                    code_id=code,
                    card_number=n,
                    card_name=f"{code}-{n}",
                )
            )
    db_conn.commit()
    return coll.collection_id


def test_build_validator_loads_codes_from_db(
    db_conn: sqlite3.Connection,
) -> None:
    """Los códigos de la DB pasan a `valid_codes`."""
    cid = _seed_collection_with_codes(db_conn, codes_and_max=[("ARG", 20), ("BRA", 18), ("KOR", 6)])
    v = build_validator(cid, db_conn)
    assert v.valid_codes == frozenset({"ARG", "BRA", "KOR"})


def test_build_validator_loads_max_numbers_from_db(
    db_conn: sqlite3.Connection,
) -> None:
    """`max_number_by_code` refleja el max(card_number) por código."""
    cid = _seed_collection_with_codes(db_conn, codes_and_max=[("ARG", 20), ("BRA", 18), ("KOR", 6)])
    v = build_validator(cid, db_conn)
    assert v.max_number_by_code == {"ARG": 20, "BRA": 18, "KOR": 6}


def test_build_validator_validates_against_db_catalog(
    db_conn: sqlite3.Connection,
) -> None:
    """End-to-end: build + validar usando solo datos de la DB."""
    cid = _seed_collection_with_codes(db_conn, codes_and_max=[("ARG", 20), ("KOR", 6)])
    v = build_validator(cid, db_conn)
    assert v.validar_codigo("KORG") == "KOR 6"
    assert v.validar_codigo("ARG20") == "ARG 20"
    # FWC no está en este catálogo → None (cae en el universo desconocido).
    assert v.validar_codigo("FWC10") is None
    # KOR99: 99 y 9 ambos exceden el max KOR=6 → None.
    assert v.validar_codigo("KOR99") is None


def test_build_validator_empty_collection_rejects_everything(
    db_conn: sqlite3.Connection,
) -> None:
    """Validador construido desde collection sin cards rechaza todo."""
    headers = CodeHeadersRepository(db_conn)
    collections = CollectionsRepository(db_conn)
    h = headers.create(CodeHeader(code_header_id=None, code_header_name="H"))
    assert h.code_header_id is not None
    coll = collections.create(
        Collection(
            collection_id=None,
            collection_name="Empty",
            card_count=0,
            requires_code=True,
            code_field_name="X",
            code_header_id=h.code_header_id,
        )
    )
    assert coll.collection_id is not None
    db_conn.commit()
    v = build_validator(coll.collection_id, db_conn)
    assert v.validar_codigo("KOR6") is None
    assert v.validar_codigo("ARG20") is None
