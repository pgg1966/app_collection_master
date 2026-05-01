"""Servicios: orquestan repositorios para lógica que cruza tablas."""

from collections_app.core.services.collections_service import CollectionsService
from collections_app.core.services.inventory_service import (
    AmbiguousCardError,
    InventoryService,
)
from collections_app.core.services.license_service import (
    SETTING_KEY_LICENSE_PREFIX,
    LicenseService,
    LicenseValidator,
    LocalHashLicenseValidator,
)
from collections_app.core.services.pdf_generator import (
    AlbumConfig,
    CardSlotData,
    PdfAlbumGenerator,
)
from collections_app.core.services.reports_service import (
    ReportsService,
    TransactionWithCard,
)
from collections_app.core.services.settings_service import (
    SETTING_KEY_ACTIVE_COLLECTION,
    SettingsService,
)

__all__ = [
    "SETTING_KEY_ACTIVE_COLLECTION",
    "SETTING_KEY_LICENSE_PREFIX",
    "AlbumConfig",
    "AmbiguousCardError",
    "CardSlotData",
    "CollectionsService",
    "InventoryService",
    "LicenseService",
    "LicenseValidator",
    "LocalHashLicenseValidator",
    "PdfAlbumGenerator",
    "ReportsService",
    "SettingsService",
    "TransactionWithCard",
]
