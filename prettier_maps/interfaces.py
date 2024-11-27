from abc import abstractmethod
from enum import Enum, unique
from typing import Any, Protocol, runtime_checkable

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction, QWidget


class IQgisInterface(QObject):  # type: ignore[misc]
    @abstractmethod
    def mainWindow(self) -> QWidget | None: ...
    @abstractmethod
    def addWebToolBarIcon(self, qAction: QAction | None) -> int: ...  # noqa: N803
    @abstractmethod
    def removeWebToolBarIcon(self, qAction: QAction | None) -> None: ...  # noqa: N803


@unique
class QueryType(Enum):
    NotSpatial = "NotSpatial"
    BBox = "BBox"
    InArea = "InArea"
    AroundArea = "AroundArea"


class OsmType(Enum):
    NODE = 1
    WAY = 2
    RELATION = 3


class Format(Enum):
    GEOJSON = 1
    SHAPEFILE = 2
    KML = 3


@runtime_checkable
class ProcessQuickQueryProtocol(Protocol):
    def __call__(
        self,
        description: str | None = None,
        type_multi_request: list[Any] | None = None,
        query_type: QueryType | None = None,
        key: str | list[str] | None = None,
        value: str | list[str] | None = None,
        area: str | None = None,
        distance: int | None = None,
        osm_objects: list[OsmType] | None = None,
        metadata: str = "body",
        timeout: int = 25,
        output_directory: str | None = None,
        output_format: Format | None = None,
        prefix_file: str | None = None,
        layer_name: str | None = None,
        white_list_values: dict[Any, Any] | None = None,
        output_geometry_types: list[Any] | None = None,
        config_outputs: dict[Any, Any] | None = None,
    ) -> int: ...
