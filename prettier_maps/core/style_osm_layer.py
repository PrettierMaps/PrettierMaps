from typing import TYPE_CHECKING

from PyQt5.QtGui import QColor

from prettier_maps.core.quick_osm_utils import is_quick_osm_layer

if TYPE_CHECKING:
    from qgis.core import QgsVectorLayer


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

        if not is_quick_osm_layer(layer):
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
    from qgis.utils import iface

    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
