from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Union

import qgis.processing as processing

from prettier_maps.core.utils import get_each_style, get_qgis_project

if TYPE_CHECKING:
    from qgis.core import QgsProject, QgsRectangle, QgsVectorTileLayer
    from qgis.gui import QgisInterface


def process_layer(
    layer: "QgsVectorTileLayer",
    folder_path: Path,
    extent: "QgsRectangle",
    max_zoom: int,
):
    layer_name = layer.name().replace(" ", "_")
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


def save_vector_tiles(
    folder_path: Path,
    max_zoom: int,
    iface: "QgisInterface",
    instance: Union["QgsProject", None] = None,
):
    from qgis.core import (
        QgsLayerTreeGroup,
        QgsVectorTileBasicRenderer,
        QgsVectorTileLayer,
    )

    instance = instance or get_qgis_project()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None
    extra_layers: list[QgsVectorTileLayer] = []

    for parent in root.children():
        if not isinstance(parent, QgsLayerTreeGroup):
            continue

        for map_layer, styles in get_each_style(parent):
            for style in styles:
                new_map_layer = map_layer.clone()
                if new_map_layer is None:
                    continue
                new_map_layer.setName(f"{style.layerName()}__{style.styleName()}")
                renderer = new_map_layer.renderer()
                if renderer is None:
                    continue
                assert isinstance(renderer, QgsVectorTileBasicRenderer)
                renderer.setStyles([style])
                extra_layers.append(new_map_layer)

    map_canvas = iface.mapCanvas()
    if map_canvas is None:
        return
    extent = map_canvas.extent()

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_layer, layer, folder_path, extent, max_zoom)
            for layer in extra_layers
        ]
        for future in futures:
            future.result()


def load_vector_tiles(
    folder_path: Path,
    instance: Union["QgsProject", None] = None,
) -> None:
    from qgis.core import QgsLayerTreeGroup, QgsVectorTileLayer

    instance = instance or get_qgis_project()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None

    main_layer = QgsLayerTreeGroup("new_layer", checked=True)

    for file in folder_path.glob("*.mbtiles"):
        print(f"Loading {file}")
        layer = QgsVectorTileLayer(f"type=mbtiles&url={file!s}", file.stem)
        main_layer.addLayer(layer)
        instance.addMapLayer(layer, False)

    root.addChildNode(main_layer)
