import json
from pathlib import Path
from typing import TYPE_CHECKING, List, Union, cast

import qgis.processing as processing
from typing_extensions import TypedDict

from prettier_maps.core.utils import get_each_style, get_qgis_project, refresh_layer

if TYPE_CHECKING:
    from qgis.core import QgsProject, QgsRectangle, QgsVectorTileLayer
    from qgis.gui import QgisInterface


def _get_layer_name(layer: "QgsVectorTileLayer") -> str:
    return str(layer.name()).replace(" ", "_")


def _get_json_file_name(layer_name: str) -> str:
    return f"{layer_name}_layers.json"


def process_layer(
    layer: "QgsVectorTileLayer",
    folder_path: Path,
    extent: "QgsRectangle",
    max_zoom: int,
):
    layer_name = _get_layer_name(layer)
    output_path = folder_path / f"{layer_name}.mbtiles"
    if output_path.exists():
        output_path.unlink()
    processing.run(
        "native:downloadvectortiles",
        parameters={
            "INPUT": layer,
            "OUTPUT": str(output_path),
            "EXTENT": extent,
            "MAX_ZOOM": max_zoom,
            "TILE_LIMIT": 10_000,
        },
    )
    print(f"Saved {layer.name()} to {output_path} with {max_zoom=}")


class RawStyle(TypedDict):
    layer_name: str
    style_name: str
    filter_expression: str
    geometry_type: int
    max_zoom_level: int
    min_zoom_level: int


def save_vector_tiles(
    folder_path: Path,
    max_zoom: int,
    iface: "QgisInterface",
    instance: Union["QgsProject", None] = None,
):
    from qgis.core import QgsLayerTreeGroup, QgsVectorTileLayer

    instance = instance or get_qgis_project()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None
    extra_layers: list[QgsVectorTileLayer] = []

    for parent in root.children():
        if not isinstance(parent, QgsLayerTreeGroup):
            continue
        for map_layer, styles in get_each_style(parent):
            extra_layers.append(map_layer)
            json_data: List[RawStyle] = [
                {
                    "layer_name": style.layerName(),
                    "style_name": style.styleName(),
                    "filter_expression": style.filterExpression(),
                    "geometry_type": style.geometryType(),
                    "max_zoom_level": style.maxZoomLevel(),
                    "min_zoom_level": style.minZoomLevel(),
                }
                for style in styles
            ]

            json_file_name = _get_json_file_name(_get_layer_name(map_layer))

            with (folder_path / json_file_name).open("w") as json_file:
                json.dump(json_data, json_file, indent=4)

    map_canvas = iface.mapCanvas()
    if map_canvas is None:
        return
    extent = map_canvas.extent()

    for extra_layer in extra_layers:
        process_layer(extra_layer, folder_path, extent, max_zoom)


def load_vector_tiles(
    folder_path: Path,
    instance: Union["QgsProject", None] = None,
) -> None:
    from qgis.core import (
        Qgis,
        QgsLayerTreeGroup,
        QgsVectorTileBasicRenderer,
        QgsVectorTileBasicRendererStyle,
        QgsVectorTileLayer,
    )

    instance = instance or get_qgis_project()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None

    main_layer = QgsLayerTreeGroup("new_layer", checked=True)

    for file in folder_path.glob("*.mbtiles"):
        with (folder_path / _get_json_file_name(file.stem)).open() as json_file:
            json_data = json.load(json_file)

        geom_types = [
            Qgis.GeometryType.Point,
            Qgis.GeometryType.Line,
            Qgis.GeometryType.Polygon,
            Qgis.GeometryType.Unknown,
            Qgis.GeometryType.Null,
        ]

        raw_style_data = cast(List[RawStyle], json_data)
        layer = QgsVectorTileLayer(f"type=mbtiles&url={file!s}", file.stem)
        renderer = QgsVectorTileBasicRenderer()
        styles: list[QgsVectorTileBasicRendererStyle] = []
        for style_data in raw_style_data:
            style = QgsVectorTileBasicRendererStyle()
            style.setGeometryType(geom_types[style_data["geometry_type"]])
            style.setStyleName(style_data["style_name"])
            style.setLayerName(style_data["layer_name"])
            style.setFilterExpression(style_data["filter_expression"])
            style.setMaxZoomLevel(style_data["max_zoom_level"])
            style.setMinZoomLevel(style_data["min_zoom_level"])
            styles.append(style)
        renderer.setStyles(styles)
        layer.setRenderer(renderer)
        main_layer.addLayer(layer)
        instance.addMapLayer(layer, False)

    root.addChildNode(main_layer)
