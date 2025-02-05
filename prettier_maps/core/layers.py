from qgis.core import (
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsProject,
    QgsVectorTileBasicRenderer,
    QgsVectorTileBasicRendererStyle,
    QgsVectorTileLayer,
)


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


def _get_qgis_project() -> Optional[QgsProject]:
    """Returns the current QGIS project.

    :return: The current QGIS project
    """

    return QgsProject.instance()


def filter_layers(
    layers_to_turn_on: set[str], instance_to_filter: Optional[QgsProject] = None
) -> None:
    """Given a set of layers, shows only those layers while hiding others.

    :param layers_to_turn_on: Set of layers to be shown
    :param instance_to_filter: Instance of a QGISProject to filter
      on. If not provided, the current QGIS project is used instead.
    """

    # Select the project instance
    instance = instance_to_filter or _get_qgis_project()
    instance = instance_to_filter or _get_qgis_project()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None

    for child in root.children():
        if not isinstance(child, QgsLayerTreeGroup):
            continue

        # Get the layer elements
        vector_tile_layers = get_layers_from_group(child)
        for layer in vector_tile_layers:
            map_layer = layer.layer()
            if not isinstance(map_layer, QgsVectorTileLayer):
                continue

            # Get the layer renderer
            renderer = map_layer.renderer()
            assert renderer is not None
            assert isinstance(renderer, QgsVectorTileBasicRenderer)
            assert isinstance(renderer, QgsVectorTileBasicRenderer)

            # Enable and disable the styles based on whether they're on the layers_to_turn_ on list
            styles = renderer.styles()
            new_styles: list[QgsVectorTileBasicRendererStyle] = []
            for style in styles:
                if style.layerName() in layers_to_turn_on:
                    style.setEnabled(True)
                else:
                    style.setEnabled(False)
                new_styles.append(style)

            renderer.setStyles(new_styles)
            # Lastly, refresh the layer
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
    from qgis.utils import iface

    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
