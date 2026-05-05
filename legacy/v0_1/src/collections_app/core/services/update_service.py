"""Servicio de detección de actualizaciones de la app.

Diseño: la fuente de updates está abstraída via `UpdateSource` (Protocol).
Hoy se usa `GitHubUpdateSource` (consulta GitHub Releases API). Para
cambiar a un servidor propio en el futuro, solo hace falta inyectar
`ServerUpdateSource(...)` en `UpdateService(source=...)` — el resto
del código (worker en main.py, banner UI, sección Acerca de) sigue
funcionando sin tocar nada más.

El protocolo es deliberadamente mínimo: `fetch_latest()` retorna el JSON
del release o `None` si la fuente falla. NO levanta excepciones — los
errores de red son normales (sin internet, GitHub caído, rate limit) y
no deben romper el flujo del usuario.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

import requests
from packaging.version import InvalidVersion, Version

from collections_app.__version__ import __update_url__, __version__

logger = logging.getLogger(__name__)

# Timeout deliberadamente corto: el chequeo es opcional. Si tarda más,
# es preferible asumir "sin red" y no bloquear al usuario.
CHECK_TIMEOUT = 8


@dataclass(frozen=True)
class UpdateInfo:
    """Resultado del chequeo de actualizaciones.

    `is_newer` ya está pre-calculado contra `__version__` actual — la UI
    no debería re-comparar versions. `download_url` es la URL directa al
    `.exe` si existe entre los assets, o cae al `release_url` (página
    HTML del release) como fallback.
    """

    current_version: str
    latest_version: str
    download_url: str
    release_url: str
    release_notes: str
    is_newer: bool


@runtime_checkable
class UpdateSource(Protocol):
    """Protocolo para fuentes de actualizaciones.

    Implementaciones:
      - GitHubUpdateSource: usa GitHub Releases API (hoy)
      - ServerUpdateSource: usa servidor propio (futuro)

    El servidor propio debe exponer un endpoint GET que devuelva el
    mismo formato JSON que GitHub Releases, o al menos los campos:
      tag_name, html_url, body, assets[].name, assets[].browser_download_url
    """

    def fetch_latest(self) -> dict[str, Any] | None:
        """Retorna el JSON del release más reciente, o None si falla.

        NUNCA debe lanzar excepciones — capturar todo error de red y
        retornar None. La UI interpreta None como "no se pudo verificar".
        """
        ...


class GitHubUpdateSource:
    """Fuente de actualizaciones via GitHub Releases API.

    URL configurada por default en `__version__.__update_url__`. Pasar
    una URL custom es útil para tests (apuntar a un mock server) o si
    se quiere consultar un repo distinto al configurado en el proyecto.
    """

    def __init__(self, url: str = __update_url__) -> None:
        self._url = url

    def fetch_latest(self) -> dict[str, Any] | None:
        try:
            r = requests.get(
                self._url,
                timeout=CHECK_TIMEOUT,
                headers={
                    "Accept": "application/vnd.github+json",
                    "User-Agent": "CollectionsApp",
                },
            )
            if r.status_code != 200:
                logger.debug("GitHubUpdateSource HTTP %s", r.status_code)
                return None
            data: dict[str, Any] = dict(r.json())
            return data
        except Exception as exc:  # noqa: BLE001 — la API debe ser silenciosa
            logger.debug("GitHubUpdateSource fetch failed: %s", exc)
            return None


class ServerUpdateSource:
    """Fuente de actualizaciones via servidor propio (futuro).

    El servidor debe exponer:
      GET <server_url>/api/v1/updates/latest
      Authorization: Bearer <api_key>   (solo si api_key no es vacío)

    Respuesta esperada (mismo formato que GitHub Releases):
        {
          "tag_name": "v1.2.0",
          "html_url": "https://tuservidor.com/releases/v1.2.0",
          "body": "Changelog...",
          "assets": [
            {
              "name": "collections-client.exe",
              "browser_download_url": "https://tuservidor.com/dl/v1.2.0/collections-client.exe"
            }
          ]
        }
    """

    def __init__(self, server_url: str, api_key: str = "") -> None:
        self._url = server_url.rstrip("/") + "/api/v1/updates/latest"
        self._api_key = api_key

    def fetch_latest(self) -> dict[str, Any] | None:
        headers: dict[str, str] = {"User-Agent": "CollectionsApp"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        try:
            r = requests.get(self._url, timeout=CHECK_TIMEOUT, headers=headers)
            if r.status_code != 200:
                logger.debug("ServerUpdateSource HTTP %s", r.status_code)
                return None
            data: dict[str, Any] = dict(r.json())
            return data
        except Exception as exc:  # noqa: BLE001 — la API debe ser silenciosa
            logger.debug("ServerUpdateSource fetch failed: %s", exc)
            return None


class UpdateService:
    """Servicio de detección de actualizaciones.

    Usa `UpdateSource` (Protocol) para abstraer la fuente. Por defecto
    usa `GitHubUpdateSource`. Para usar servidor propio:

        service = UpdateService(
            source=ServerUpdateSource(
                server_url=settings.get("server_url"),
                api_key=settings.get("server_api_key") or "",
            )
        )
    """

    def __init__(self, source: UpdateSource | None = None) -> None:
        self._source: UpdateSource = source if source is not None else GitHubUpdateSource()

    def check_for_updates(self) -> UpdateInfo | None:
        """Verifica si hay una versión más nueva disponible.

        Retorna:
          - `UpdateInfo` con el resultado (puede tener `is_newer=False`
            si estamos al día — sirve para mostrar "estás actualizado").
          - `None` si la fuente falló (sin red, JSON inválido, version
            no parseable). La UI debe mostrar "no se pudo verificar".

        NO levanta excepciones.
        """
        data = self._source.fetch_latest()
        if not data:
            return None

        latest_tag = str(data.get("tag_name", "")).lstrip("v")
        if not latest_tag:
            return None

        try:
            current = Version(__version__)
            latest = Version(latest_tag)
        except InvalidVersion as exc:
            logger.debug("Version parse failed: %s", exc)
            return None

        # Buscar asset .exe; si no hay, caer a la página HTML del release.
        assets = data.get("assets", []) or []
        exe_asset = next(
            (a for a in assets if str(a.get("name", "")).endswith(".exe")),
            None,
        )
        release_url = str(data.get("html_url", ""))
        download_url = str(exe_asset["browser_download_url"]) if exe_asset else release_url

        return UpdateInfo(
            current_version=str(current),
            latest_version=str(latest),
            download_url=download_url,
            release_url=release_url,
            release_notes=str(data.get("body", ""))[:500],
            is_newer=latest > current,
        )
