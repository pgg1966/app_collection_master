"""Versión y metadatos de la aplicación.

Mantener `__version__` sincronizado con `pyproject.toml`. La política
del proyecto: SemVer (`MAJOR.MINOR.PATCH`) — `packaging.version.Version`
hace la comparación, así que `1.10.0 > 1.9.0` (no comparación lexicográfica).

`__update_url__` apunta a la fuente activa de actualizaciones. Hoy es
GitHub Releases. Para migrar a un servidor propio en el futuro, basta
con cambiar esta URL — el endpoint debe devolver el mismo JSON que
GitHub Releases (campos `tag_name`, `html_url`, `body`, `assets[]`).
"""

__version__ = "1.0.0"
__app_name__ = "CollectionsApp"

# Repo de GitHub usado por GitHubUpdateSource. Reemplazar por el repo real
# cuando se publique el primer release.
__github_repo__ = "tuusuario/collections"
__update_url__ = f"https://api.github.com/repos/{__github_repo__}/releases/latest"
