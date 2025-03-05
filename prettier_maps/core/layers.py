from typing import Optional

from PyQt5.QtGui import QColor
from qgis.core import (
    QgsFillSymbol,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsLayerTreeNode,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsProject,
    QgsVectorLayer,
    QgsVectorTileBasicRenderer,
    QgsVectorTileBasicRendererStyle,
    QgsVectorTileLayer,
)
from qgis.utils import iface


def get_layers_from_group(group: QgsLayerTreeGroup) -> list[QgsLayerTreeLayer]:
    """Returns the direct descendant layers from a given QgsLayerTreeGroup.

    :param group: The group to get the descendant layers from
    :return: The direct descendant layers from group
    """

    return [layer for layer in group.children() if isinstance(layer, QgsLayerTreeLayer)]


def refresh_layer(
    layer: QgsVectorTileLayer, renderer: QgsVectorTileBasicRenderer
) -> None:
    """Refreshes a certain layer.

    :param layer: Layer to refresh
    :param renderer: The renderer that will be used for the layer
    """

    layer.setRenderer(renderer.clone())
    layer.setBlendMode(layer.blendMode())
    layer.setOpacity(layer.opacity())


def _get_groups(project: Optional[QgsProject] = None) -> list[QgsLayerTreeNode]:
    instance = project or QgsProject.instance()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None

    return root.children()


def filter_layers(
    layers_to_turn_on: set[str], instance_to_filter: Optional[QgsProject] = None
) -> None:
    """Given a set of layers, shows only those layers while hiding others.

    :param layers_to_turn_on: Set of layers to be shown
    :param instance_to_filter: Instance of a QGISProject to filter
      on. If not provided, the current QGIS project is used instead.
    """

    for child in _get_groups(project=instance_to_filter):
        if not isinstance(child, QgsLayerTreeGroup):
            continue

        for layer in get_layers_from_group(child):
            map_layer = layer.layer()
            if not isinstance(map_layer, QgsVectorTileLayer):
                continue
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
    for child in _get_groups():
        if not isinstance(child, QgsLayerTreeLayer):
            continue
        layer = child.layer()

        # Checks if a certain layer comes from a QuickOSM query
        variable_names = layer.customProperty("variableNames")
        if variable_names is None:
            continue
        if "quickosm_query" not in variable_names:
            continue

        style_single_layer(layer)
        update_styled_layer(layer)


def style_single_layer(layer: QgsVectorLayer) -> None:
    """Applies a styling to a certain layer

    :param layer: layer to style
    """

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


def update_styled_layer(layer: QgsVectorLayer) -> None:
    """Refreshes a layer to reapply the changes.

    :param layer: layer to update
    """

    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
