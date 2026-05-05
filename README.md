# Collections

Aplicación para gestionar colecciones de cards/figuritas.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # o .venv\Scripts\activate en Windows
pip install -e ".[dev]"
```

## Uso

Aplicación admin (configuración):
```bash
collections-admin
```

Aplicación cliente (uso final):
```bash
collections-client
```

## Desarrollo

```bash
pytest                    # correr tests
black src/ tests/         # formatear
ruff check src/ tests/    # lint
mypy src/                 # validar tipos
```
# app_collection_master
