"""Entry point de la aplicación admin (configuración)."""

import logging

from collections_app.core.utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)


def main() -> int:
    """Entry point. Por ahora solo inicializa logging."""
    setup_logging(level=logging.DEBUG)
    logger.info("Admin app — bootstrap OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
