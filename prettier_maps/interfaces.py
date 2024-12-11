from abc import abstractmethod
from enum import Enum, unique
from typing import Any, Protocol, runtime_checkable

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction, QWidget
from typing import Union


class IQgisInterface(QObject):  # type: ignore[misc]
    @abstractmethod
    def mainWindow(self) -> Union[QWidget, None]: ...
    @abstractmethod
    def addWebToolBarIcon(self, qAction: Union[QAction, None]) -> int: ...  # noqa: N803
    @abstractmethod
    def removeWebToolBarIcon(self, qAction: Union[QAction, None]) -> None: ...  # noqa: N803


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
        description: Union[str, None] = None,
        type_multi_request: Union[list[Any], None] = None,
        query_type: Union[QueryType, None] = None,
        key: Union[str, list[str], None] = None,
        value: Union[str, list[str], None] = None,
        area: Union[str, None] = None,
        distance: Union[int, None] = None,
        osm_objects: Union[list[OsmType], None] = None,
        metadata: str = "body",
        timeout: int = 25,
        output_directory: Union[str, None] = None,
        output_format: Union[Format, None] = None,
        prefix_file: Union[str, None] = None,
        layer_name: Union[str, None] = None,
        white_list_values: Union[dict[Any, Any], None] = None,
        output_geometry_types: Union[list[Any], None] = None,
        config_outputs: Union[dict[Any, Any], None] = None,
    ) -> int: ...
