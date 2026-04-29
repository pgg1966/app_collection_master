"""ABM concreto de colecciones."""

import sqlite3

from PySide6.QtWidgets import QVBoxLayout, QWidget

from collections_app.core.models import Collection
from collections_app.core.repositories import (
    CodesHeadersRepository,
    CollectionsRepository,
)
from collections_app.core.services import CollectionsService
from collections_app.shared_ui import AbmConfig, AbmWidget, FieldDef, FieldType


class CollectionsAbmView(QWidget):
    """ABM de Collections, con combo de header y validaciones de negocio."""

    def __init__(self, conn: sqlite3.Connection, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.conn = conn

        config = AbmConfig(
            title=self.tr("ABM Colecciones"),
            module_code="COL001",
            fields=[
                FieldDef(
                    "collection_id",
                    "ID",
                    FieldType.READONLY,
                    is_id=True,
                    is_required=False,
                    grid_width=50,
                ),
                FieldDef(
                    "collection_name",
                    "Nombre",
                    FieldType.TEXT,
                    max_length=100,
                    grid_width=200,
                ),
                FieldDef(
                    "card_count",
                    "Cantidad de cards",
                    FieldType.INT,
                    grid_width=120,
                ),
                FieldDef(
                    "requires_code",
                    "Requiere código",
                    FieldType.BOOL,
                    is_required=False,
                    grid_width=130,
                ),
                FieldDef(
                    "code_field_name",
                    "Etiqueta del código",
                    FieldType.TEXT,
                    max_length=50,
                    is_required=False,
                    placeholder=self.tr("ej: Set, País"),
                    grid_width=150,
                ),
                FieldDef(
                    "code_header_id",
                    "Cabecera de código",
                    FieldType.COMBO,
                    combo_choices=self._get_header_choices,
                    grid_width=180,
                ),
                FieldDef(
                    "is_premium",
                    "Premium",
                    FieldType.BOOL,
                    is_required=False,
                    grid_width=80,
                ),
                FieldDef(
                    "license_key_required",
                    "Hash de licencia",
                    FieldType.TEXT,
                    max_length=100,
                    is_required=False,
                    show_in_grid=False,
                ),
            ],
            filter_field="collection_name",
            filter_label=self.tr("Buscar por nombre"),
            on_load_all=self._load,
            on_save=self._save,
            on_delete=self._delete,
            on_validate=self._validate,
            model_class=Collection,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.abm = AbmWidget(config)
        layout.addWidget(self.abm)

    def _get_header_choices(self) -> list[tuple[str, object]]:
        """Choices del combo "Cabecera de código", evaluado en cada uso.

        Pasamos este método como callable a `FieldDef.combo_choices` para
        que `AbmWidget` lo re-evalúe cada vez que el form se limpia o se
        carga una fila — así nuevas cabeceras creadas en otros tabs
        aparecen sin reiniciar la app.
        """
        repo = CodesHeadersRepository(self.conn)
        return [(h.code_header_name, h.code_header_id) for h in repo.list_all()]

    def _load(self) -> list[Collection]:
        return CollectionsRepository(self.conn).list_all()

    def _save(self, collection: Collection) -> Collection:
        if collection.collection_id is None:
            saved = CollectionsService(self.conn).create_collection_with_validation(collection)
        else:
            saved = CollectionsRepository(self.conn).update(collection)
        self.conn.commit()
        return saved

    def _delete(self, collection: Collection) -> bool:
        assert collection.collection_id is not None
        ok = CollectionsRepository(self.conn).delete(collection.collection_id)
        self.conn.commit()
        return ok

    def _validate(self, collection: Collection) -> tuple[bool, str]:
        if collection.requires_code and not collection.code_field_name:
            return False, self.tr("Si requiere código, debe especificarse la etiqueta del campo.")
        if collection.is_premium and not collection.license_key_required:
            return False, self.tr("Las colecciones premium deben tener hash de licencia.")
        return True, ""
