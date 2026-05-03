"""Servicios: orquestan repositorios para lógica que cruza tablas."""

from collections_app.core.services.album_service import AlbumService
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
    AlbumCard,
    PdfGeneratorResult,
    generate_album_pdf,
    generate_duplicates_pdf,
    generate_missing_pdf,
    generate_owned_pdf,
    validate_exchange_pdf_metadata,
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
    "AlbumCard",
    "AlbumService",
    "AmbiguousCardError",
    "CollectionsService",
    "InventoryService",
    "LicenseService",
    "LicenseValidator",
    "LocalHashLicenseValidator",
    "PdfGeneratorResult",
    "ReportsService",
    "SettingsService",
    "TransactionWithCard",
    "generate_album_pdf",
    "generate_duplicates_pdf",
    "generate_missing_pdf",
    "generate_owned_pdf",
    "validate_exchange_pdf_metadata",
]
