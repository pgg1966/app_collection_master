"""Repositorios: una clase por tabla, encapsulan SQL."""

from collections_app.core.repositories.base import BaseRepository
from collections_app.core.repositories.cards_repo import CardsRepository
from collections_app.core.repositories.codes_headers_repo import CodesHeadersRepository
from collections_app.core.repositories.codes_lines_repo import CodesLinesRepository
from collections_app.core.repositories.collections_repo import CollectionsRepository
from collections_app.core.repositories.inventory_repo import InventoryRepository
from collections_app.core.repositories.settings_repo import SettingsRepository
from collections_app.core.repositories.transactions_repo import TransactionsRepository

__all__ = [
    "BaseRepository",
    "CardsRepository",
    "CodesHeadersRepository",
    "CodesLinesRepository",
    "CollectionsRepository",
    "InventoryRepository",
    "SettingsRepository",
    "TransactionsRepository",
]
