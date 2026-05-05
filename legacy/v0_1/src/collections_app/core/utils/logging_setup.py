"""Configuración centralizada de logging."""

import logging
import logging.handlers
from pathlib import Path

from collections_app.core.utils.paths import get_logs_dir


def setup_logging(level: int = logging.INFO, log_filename: str = "app.log") -> None:
    """Configura logging para toda la app.

    Args:
        level: nivel de logging (logging.INFO, logging.DEBUG, etc.)
        log_filename: nombre del archivo de log
    """
    log_path: Path = get_logs_dir() / log_filename

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=2 * 1024 * 1024,  # 2 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    logging.getLogger(__name__).info("Logging inicializado en %s", log_path)
