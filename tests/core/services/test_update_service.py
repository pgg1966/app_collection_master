"""Tests del UpdateService y sus UpdateSources."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from collections_app.core.services.update_service import (
    GitHubUpdateSource,
    ServerUpdateSource,
    UpdateInfo,
    UpdateService,
    UpdateSource,
)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _mock_response(status_code: int = 200, json_data: dict | None = None) -> MagicMock:
    """Crea un mock de requests.Response con el status y JSON dados."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    return resp


def _release_payload(
    tag: str = "v1.1.0",
    html_url: str = "https://github.com/x/y/releases/tag/v1.1.0",
    body: str = "Notas del release",
    exe_url: str | None = "https://example.com/app.exe",
) -> dict:
    """Construye un payload tipo GitHub Releases para los tests."""
    assets = []
    if exe_url is not None:
        assets.append({"name": "collections-client.exe", "browser_download_url": exe_url})
    return {"tag_name": tag, "html_url": html_url, "body": body, "assets": assets}


# ----------------------------------------------------------------------
# GitHubUpdateSource
# ----------------------------------------------------------------------


def test_github_source_returns_dict_on_success():
    """fetch_latest retorna el JSON parseado cuando HTTP 200."""
    payload = _release_payload()
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, payload)
        result = GitHubUpdateSource("http://x").fetch_latest()
    assert result == payload


def test_github_source_returns_none_on_http_error():
    """HTTP 404/500/etc → None sin excepción."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(404)
        assert GitHubUpdateSource("http://x").fetch_latest() is None


def test_github_source_returns_none_on_connection_error():
    """ConnectionError → None (sin red, host no resuelve)."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("no route to host")
        assert GitHubUpdateSource("http://x").fetch_latest() is None


def test_github_source_returns_none_on_timeout():
    """Timeout → None (la red está pero GitHub no responde a tiempo)."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.side_effect = requests.Timeout("read timeout")
        assert GitHubUpdateSource("http://x").fetch_latest() is None


def test_github_source_sends_user_agent_and_accept_headers():
    """Sanity: la API de GitHub requiere User-Agent y Accept conocidos."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, _release_payload())
        GitHubUpdateSource("http://x").fetch_latest()
    headers = mock_get.call_args.kwargs["headers"]
    assert headers["User-Agent"] == "CollectionsApp"
    assert headers["Accept"] == "application/vnd.github+json"


# ----------------------------------------------------------------------
# ServerUpdateSource
# ----------------------------------------------------------------------


def test_server_source_sends_bearer_token():
    """Si hay api_key, manda header Authorization: Bearer <token>."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, _release_payload())
        ServerUpdateSource("https://srv", api_key="mytoken").fetch_latest()
    headers = mock_get.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer mytoken"


def test_server_source_no_token_no_auth_header():
    """Sin api_key NO se manda Authorization (servidor podría rechazarlo)."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, _release_payload())
        ServerUpdateSource("https://srv", api_key="").fetch_latest()
    headers = mock_get.call_args.kwargs["headers"]
    assert "Authorization" not in headers


def test_server_source_appends_endpoint_path():
    """La URL final debe ser <server_url>/api/v1/updates/latest."""
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, _release_payload())
        ServerUpdateSource("https://srv/", api_key="").fetch_latest()
    assert mock_get.call_args.args[0] == "https://srv/api/v1/updates/latest"


def test_server_source_returns_none_on_http_error():
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.return_value = _mock_response(401)
        assert ServerUpdateSource("https://srv").fetch_latest() is None


def test_server_source_returns_none_on_exception():
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        mock_get.side_effect = requests.ConnectionError("nope")
        assert ServerUpdateSource("https://srv").fetch_latest() is None


# ----------------------------------------------------------------------
# Protocol satisfaction
# ----------------------------------------------------------------------


def test_update_source_protocol_satisfied_by_implementations():
    """Las dos implementaciones cumplen el Protocol UpdateSource (runtime check)."""
    assert isinstance(GitHubUpdateSource("http://x"), UpdateSource)
    assert isinstance(ServerUpdateSource("http://x"), UpdateSource)


# ----------------------------------------------------------------------
# UpdateService — composición e inyección
# ----------------------------------------------------------------------


class _FakeSource:
    """UpdateSource stub para tests: retorna lo que se le configura."""

    def __init__(self, payload: dict | None) -> None:
        self.payload = payload
        self.calls = 0

    def fetch_latest(self) -> dict | None:
        self.calls += 1
        return self.payload


def test_update_service_uses_injected_source():
    """UpdateService.check_for_updates() consulta la fuente inyectada (no requests reales)."""
    fake = _FakeSource(_release_payload(tag="v2.0.0"))
    with patch("collections_app.core.services.update_service.requests.get") as mock_get:
        result = UpdateService(source=fake).check_for_updates()
    assert fake.calls == 1
    mock_get.assert_not_called()
    assert result is not None
    assert result.latest_version == "2.0.0"


def test_check_returns_none_when_source_returns_none():
    """Sin red / fuente caída: check_for_updates retorna None."""
    assert UpdateService(source=_FakeSource(None)).check_for_updates() is None


def test_check_returns_none_when_tag_missing():
    """Payload sin tag_name → None (no podemos comparar versions)."""
    fake = _FakeSource({"html_url": "x", "body": "y", "assets": []})
    assert UpdateService(source=fake).check_for_updates() is None


def test_check_returns_none_when_tag_invalid():
    """tag_name no parseable como Version → None."""
    fake = _FakeSource(_release_payload(tag="not-a-version"))
    assert UpdateService(source=fake).check_for_updates() is None


# ----------------------------------------------------------------------
# UpdateService — comparación de versiones
# ----------------------------------------------------------------------


def _patch_current(version: str):
    """Helper: parchea __version__ tal como lo lee update_service."""
    return patch("collections_app.core.services.update_service.__version__", version)


def test_check_returns_is_newer_true():
    fake = _FakeSource(_release_payload(tag="v1.1.0"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.is_newer is True
    assert info.current_version == "1.0.0"
    assert info.latest_version == "1.1.0"


def test_check_returns_is_newer_false_same_version():
    fake = _FakeSource(_release_payload(tag="v1.0.0"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.is_newer is False


def test_check_returns_is_newer_false_older():
    """Si lo "último" del servidor es viejo, no es nueva."""
    fake = _FakeSource(_release_payload(tag="v0.9.0"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.is_newer is False


def test_version_semver_comparison_not_lexicographic():
    """Regresión: '1.10.0' > '1.9.0' (string comparison sería al revés)."""
    fake = _FakeSource(_release_payload(tag="v1.10.0"))
    with _patch_current("1.9.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.is_newer is True


def test_tag_v_prefix_stripped():
    """tag_name='v2.0.0' → latest_version='2.0.0'."""
    fake = _FakeSource(_release_payload(tag="v2.0.0"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.latest_version == "2.0.0"


def test_tag_without_v_prefix_also_works():
    """tag_name sin 'v' debe funcionar igual."""
    fake = _FakeSource(_release_payload(tag="2.0.0"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.latest_version == "2.0.0"


# ----------------------------------------------------------------------
# UpdateService — selección de download_url
# ----------------------------------------------------------------------


def test_exe_asset_url_preferred():
    """Si hay un .exe entre los assets, usar su browser_download_url."""
    fake = _FakeSource(_release_payload(tag="v1.1.0", exe_url="https://example.com/app.exe"))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.download_url == "https://example.com/app.exe"


def test_no_exe_asset_falls_back_to_html_url():
    """Sin .exe en assets, download_url == release_url (página HTML)."""
    fake = _FakeSource(
        _release_payload(tag="v1.1.0", html_url="https://github.com/x/y/r/v1", exe_url=None)
    )
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert info.download_url == info.release_url
    assert info.download_url == "https://github.com/x/y/r/v1"


def test_release_notes_truncated_to_500_chars():
    """Notas largas se cortan a 500 chars (banner / about no necesitan más)."""
    long_body = "a" * 1000
    fake = _FakeSource(_release_payload(tag="v1.1.0", body=long_body))
    with _patch_current("1.0.0"):
        info = UpdateService(source=fake).check_for_updates()
    assert info is not None
    assert len(info.release_notes) == 500


# ----------------------------------------------------------------------
# UpdateInfo dataclass
# ----------------------------------------------------------------------


def test_update_info_is_frozen():
    """UpdateInfo es @dataclass(frozen=True): no se puede mutar."""
    info = UpdateInfo(
        current_version="1.0.0",
        latest_version="1.1.0",
        download_url="x",
        release_url="y",
        release_notes="z",
        is_newer=True,
    )
    from dataclasses import FrozenInstanceError

    with pytest.raises(FrozenInstanceError):
        info.is_newer = False  # type: ignore[misc]
