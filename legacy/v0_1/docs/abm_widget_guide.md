# Guía del AbmWidget genérico

`AbmWidget` es un widget reutilizable que implementa el patrón filtro + grilla
+ formulario para alta/baja/modificación de cualquier dataclass. La idea es
que para escribir un ABM nuevo configurás campos y callbacks, no copiás
código de otro ABM.

## Estructura

```python
from collections_app.shared_ui import (
    AbmWidget, AbmConfig, FieldDef, FieldType,
)
```

- **`FieldType`** — enum de tipos de input (`TEXT`, `INT`, `BOOL`, `COMBO`,
  `READONLY`).
- **`FieldDef`** — describe un campo del modelo + cómo renderizarlo.
- **`AbmConfig`** — bundle con la lista de campos, los callbacks de
  persistencia y la clase del modelo a instanciar.
- **`AbmWidget`** — el `QWidget` que se monta en una ventana o tab.

## FieldDef en detalle

```python
FieldDef(
    name="...",                   # debe coincidir con un atributo del modelo
    label="...",                  # texto visible (i18n con tr())
    field_type=FieldType.TEXT,
    is_id=False,                  # True si forma parte de la PK
    is_required=True,             # bloquea Guardar si está vacío
    max_length=None,              # solo TEXT
    combo_choices=None,           # [(label, value), ...] para COMBO
    placeholder="",
    show_in_grid=True,            # False oculta la columna en la grilla
    grid_width=None,              # px; si None usa Interactive
)
```

### Tabla de tipos

| FieldType | Input renderizado | Valor leído                      |
|-----------|-------------------|----------------------------------|
| TEXT      | `QLineEdit`       | `str` (vacío → `None`)           |
| INT       | `QSpinBox`        | `int` (rango 0–999.999)          |
| BOOL      | `QCheckBox`       | `bool`                           |
| COMBO     | `QComboBox`       | el `value` de `combo_choices`    |
| READONLY  | `QLineEdit` gris  | nunca se edita; mantiene valor   |

### Comportamiento de PKs

- **PK auto-id (numérica)**: declarala como `READONLY` + `is_id=True`. El
  widget la deja siempre gris y no envía valor en `extra_kwargs`. El
  repository asigna el id en `create()`.
- **PK significativa (texto)**: declarala como `TEXT` + `is_id=True`. El
  widget la mantiene editable solo cuando se está creando un registro
  nuevo y la pasa a readonly al cargar una fila existente.

## AbmConfig en detalle

```python
@dataclass
class AbmConfig:
    title: str                      # Header oscuro: "Módulo: {title} (...)"
    module_code: str                # Código corto, ej "COL001"
    fields: list[FieldDef]
    on_load_all: Callable[[], list[Any]]
    on_save: Callable[[Any], Any]   # debe retornar el modelo persistido
    on_delete: Callable[[Any], bool]
    model_class: type               # ej Collection
    list_label: str = "Listado"
    edit_label: str = "Edición"
    filter_label: str = "Buscar"
    filter_field: str | None = None  # campo del modelo para filtrar (None=todos)
    on_validate: Callable[[Any], tuple[bool, str]] | None = None
    extra_kwargs: dict[str, Any] = field(default_factory=dict)
```

### Callbacks

- `on_load_all()` — retorna todos los registros para mostrar.
- `on_save(record)` — persiste y retorna el modelo (con `id` poblado si era
  nuevo). Debe **commitear** la conexión SQLite.
- `on_delete(record)` — borra y retorna `True` si efectivamente borró. Debe
  **commitear**.
- `on_validate(record)` — opcional. Devuelve `(ok, razón)`. Si `ok=False`,
  el widget muestra `razón` en el status label sin guardar.

### `extra_kwargs`

Útil cuando el modelo recibe campos que no se editan en el formulario
(ej. `collection_id` cuando estás haciendo el ABM de cards de una
colección específica). Se pasan como kwargs al instanciar `model_class`.

## Ejemplos

### ABM de Collections

```python
from collections_app.core.models import Collection
from collections_app.core.services import CollectionsService
from collections_app.core.repositories import (
    CollectionsRepository, CodesHeadersRepository,
)
from collections_app.shared_ui import AbmConfig, AbmWidget, FieldDef, FieldType


def build_collections_abm(conn) -> AbmWidget:
    headers_repo = CodesHeadersRepository(conn)
    collections_repo = CollectionsRepository(conn)
    service = CollectionsService(conn)

    code_choices = [(h.code_header_name, h.code_header_id) for h in headers_repo.list_all()]

    def _save(collection: Collection) -> Collection:
        if collection.collection_id is None:
            saved = service.create_collection_with_validation(collection)
        else:
            saved = collections_repo.update(collection)
        conn.commit()
        return saved

    def _delete(collection: Collection) -> bool:
        ok = collections_repo.delete(collection.collection_id)
        conn.commit()
        return ok

    config = AbmConfig(
        title="Colecciones",
        module_code="COL001",
        fields=[
            FieldDef("collection_id", "ID", FieldType.READONLY, is_id=True, is_required=False),
            FieldDef("collection_name", "Nombre", FieldType.TEXT, max_length=80),
            FieldDef("card_count", "Cards", FieldType.INT),
            FieldDef("requires_code", "Usa código", FieldType.BOOL, is_required=False),
            FieldDef("code_field_name", "Etiqueta", FieldType.TEXT, is_required=False),
            FieldDef("code_header_id", "Header", FieldType.COMBO, combo_choices=code_choices),
            FieldDef("is_premium", "Premium", FieldType.BOOL, is_required=False, show_in_grid=False),
            FieldDef(
                "license_key_required", "Licencia",
                FieldType.TEXT, is_required=False, show_in_grid=False,
            ),
        ],
        on_load_all=collections_repo.list_all,
        on_save=_save,
        on_delete=_delete,
        model_class=Collection,
        filter_field="collection_name",
    )
    return AbmWidget(config)
```

### ABM de CodesHeaders

```python
from collections_app.core.models import CodeHeader
from collections_app.core.repositories import CodesHeadersRepository
from collections_app.shared_ui import AbmConfig, AbmWidget, FieldDef, FieldType


def build_headers_abm(conn) -> AbmWidget:
    repo = CodesHeadersRepository(conn)

    def _save(header: CodeHeader) -> CodeHeader:
        if header.code_header_id is None:
            saved = repo.create(header)
        else:
            saved = repo.update(header)
        conn.commit()
        return saved

    def _delete(header: CodeHeader) -> bool:
        ok = repo.delete(header.code_header_id)
        conn.commit()
        return ok

    config = AbmConfig(
        title="Headers de códigos",
        module_code="HDR001",
        fields=[
            FieldDef("code_header_id", "ID", FieldType.READONLY, is_id=True, is_required=False),
            FieldDef("code_header_name", "Nombre", FieldType.TEXT, max_length=80),
            FieldDef("code_max_length", "Long. máx.", FieldType.INT, is_required=False),
        ],
        on_load_all=repo.list_all,
        on_save=_save,
        on_delete=_delete,
        model_class=CodeHeader,
        filter_field="code_header_name",
    )
    return AbmWidget(config)
```

### ABM de CodesLines (con `extra_kwargs`)

Cuando el ABM está scope-eado a un header padre seleccionado, no querés
exponer `code_header_id` en el formulario — lo fijás como `extra_kwargs`:

```python
config = AbmConfig(
    title="Códigos de FIFA",
    module_code="LIN001",
    fields=[
        FieldDef("code_id", "Código", FieldType.TEXT, is_id=True, max_length=3),
        FieldDef("code_name", "Nombre", FieldType.TEXT),
    ],
    on_load_all=lambda: lines_repo.list_by_header(active_header_id),
    on_save=_save_line,
    on_delete=_delete_line,
    model_class=CodeLine,
    extra_kwargs={"code_header_id": active_header_id},
    filter_field="code_id",
)
```

## Tests

Todos los tests del AbmWidget usan `pytest-qt`. Patrón típico:

```python
def test_save_new_record(qtbot, store):
    config = _build_config(store)
    widget = AbmWidget(config)
    qtbot.addWidget(widget)
    widget.show()

    widget._inputs["name"].setText("nuevo")
    qtbot.mouseClick(widget._save_button, Qt.MouseButton.LeftButton)

    assert len(store.items) == 1
```

Para clickear filas de la grilla evitando coordenadas reales, emití el
signal `clicked` directamente con un `QModelIndex`:

```python
widget._grid_view.clicked.emit(widget._proxy_model.index(0, 0))
```

Para el diálogo de confirmación de borrado, `monkeypatch.setattr` sobre
`QMessageBox.question`:

```python
monkeypatch.setattr(
    QMessageBox, "question", lambda *a, **kw: QMessageBox.StandardButton.Yes,
)
```
