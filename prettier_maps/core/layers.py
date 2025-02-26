from collections.abc import Iterable
from typing import TYPE_CHECKING, List, Set, Tuple, Union

from PyQt5.QtGui import QColor

from prettier_maps.core.utils import get_layers_from_group, get_qgis_project

if TYPE_CHECKING:
    from qgis.core import (
        QgsLayerTreeGroup,
        QgsProject,
        QgsVectorLayer,
        QgsVectorTileBasicRenderer,
        QgsVectorTileBasicRendererStyle,
        QgsVectorTileLayer,
    )


def refresh_layer(layer: "QgsVectorTileLayer", renderer: "QgsVectorTileBasicRenderer"):
    layer.setRenderer(renderer.clone())
    layer.setBlendMode(layer.blendMode())
    layer.setOpacity(layer.opacity())


def filter_layers(
    layers_to_turn_on: Set[str], instance_to_filter: Union["QgsProject", None] = None
):
    from qgis.core import (
        QgsLayerTreeGroup,
        QgsVectorTileBasicRenderer,
        QgsVectorTileBasicRendererStyle,
        QgsVectorTileLayer,
    )

    instance = instance_to_filter or get_qgis_project()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None

    for parent in root.children():
        if not isinstance(parent, QgsLayerTreeGroup):
            continue

        vector_tile_layers = get_layers_from_group(parent)

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
            new_styles: list[QgsVectorTileBasicRendererStyle] = []
            for style in styles:
                if style.styleName() in layers_to_turn_on:
                    style.setEnabled(True)
                else:
                    style.setEnabled(False)
                new_styles.append(style)

            renderer.setStyles(new_styles)
            refresh_layer(map_layer, renderer)


def apply_style_to_quick_osm_layers() -> None:
    from qgis.core import QgsLayerTreeLayer, QgsProject

    instance = QgsProject.instance()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None

    for child in root.children():
        if not isinstance(child, QgsLayerTreeLayer):
            continue
        layer = child.layer()

        variable_names = layer.customProperty("variableNames")
        if variable_names is None:
            continue
        if "quickosm_query" not in variable_names:
            continue

        style_single_layer(layer)
        update_styled_layer(layer)


def style_single_layer(layer: "QgsVectorLayer"):
    from qgis.core import QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol

    symbol_renderer = layer.renderer()
    cur_symbol = symbol_renderer.symbol()

    basic_symbols = (QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol)
    symbol = None

    for symbol_type in basic_symbols:
        if isinstance(cur_symbol, symbol_type):
            symbol = symbol_type.createSimple({})
    # If we can't overwrite with a simple, just change the colour
    if symbol is None:
        symbol = cur_symbol

    symbol.setColor(QColor.fromRgb(155, 0, 155))
    symbol_renderer.setSymbol(symbol)


def update_styled_layer(layer: "QgsVectorLayer"):
    from qgis.gui import QgisInterface
    from qgis.utils import iface

    assert isinstance(iface, QgisInterface)

    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
