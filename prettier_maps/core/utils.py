from collections.abc import Iterable
from typing import TYPE_CHECKING, List, Tuple, Union

if TYPE_CHECKING:
    from qgis.core import (
        QgsLayerTreeGroup,
        QgsLayerTreeLayer,
        QgsProject,
        QgsVectorTileBasicRendererStyle,
        QgsVectorTileLayer,
    )


def get_qgis_project() -> Union["QgsProject", None]:
    from qgis.core import QgsProject

    return QgsProject.instance()


def get_layers_from_group(group: "QgsLayerTreeGroup") -> List["QgsLayerTreeLayer"]:
    from qgis.core import QgsLayerTreeLayer

    return [layer for layer in group.children() if isinstance(layer, QgsLayerTreeLayer)]


def get_each_style(
    tree_group_layer: "QgsLayerTreeGroup",
) -> Iterable[Tuple["QgsVectorTileLayer", List["QgsVectorTileBasicRendererStyle"]]]:
    from qgis.core import QgsVectorTileBasicRenderer, QgsVectorTileLayer

    vector_tile_layers = get_layers_from_group(tree_group_layer)

    for layer in vector_tile_layers:
        map_layer = layer.layer()
        if not isinstance(map_layer, QgsVectorTileLayer):
            continue
        renderer = map_layer.renderer()
        assert renderer is not None
        renderer = map_layer.renderer()
        assert renderer is not None

        assert isinstance(renderer, QgsVectorTileBasicRenderer)

        styles = renderer.styles()
        yield (map_layer, styles)
