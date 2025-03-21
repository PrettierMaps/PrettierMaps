from PyQt5.QtGui import QColor
from qgis.core import (
    QgsFillSymbol,
    QgsLayerTreeLayer,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsVectorLayer,
)
from qgis.utils import iface

from prettier_maps.core.layers import get_groups, is_quick_osm_layer


def apply_style_to_quick_osm_layers(colour: QColor) -> None:
    """
    Main styling function, linked to styling button. Styles all QuickOSM layers.
    """
    for child in get_groups():
        if not isinstance(child, QgsLayerTreeLayer):
            continue
        layer = child.layer()

        if is_quick_osm_layer(layer):
            style_single_layer(layer, colour)
            update_styled_layer(layer)


def style_single_layer(layer: "QgsVectorLayer", colour: QColor) -> None:
    """
    Makes an individual layer conform to the uniform style.
    """

    symbol_renderer = layer.renderer()
    cur_symbol = symbol_renderer.symbol()

    basic_symbols = (QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol)
    symbol = None

    for symbol_type in basic_symbols:
        if isinstance(cur_symbol, symbol_type):
            symbol = symbol_type.createSimple({})

    # If we can't overwrite with a simple, settle for just changing the colour
    if symbol is None:
        symbol = cur_symbol

    if colour.isValid():
        symbol.setColor(colour)
        symbol_renderer.setSymbol(symbol)
    else:
        # defaults to purple
        symbol.setColor(QColor.fromRgb(155, 0, 155))
        symbol_renderer.setSymbol(symbol)


def update_styled_layer(layer: QgsVectorLayer) -> None:
    """
    Makes QGIS show the new style.
    """

    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
