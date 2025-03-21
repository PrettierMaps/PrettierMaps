from typing import List, Optional

from qgis.core import (
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsLayerTreeNode,
    QgsProject,
    QgsVectorLayer,
    QgsVectorTileBasicRenderer,
    QgsVectorTileBasicRendererStyle,
    QgsVectorTileLayer,
)


def get_layers_from_group(group: QgsLayerTreeGroup) -> List[QgsVectorTileLayer]:
    layers = []
    for child in group.children():
        if isinstance(child, QgsLayerTreeLayer):
            layer = child.layer()
            if isinstance(layer, QgsVectorTileLayer):
                layers.append(layer)
    return layers


def refresh_layer(
    layer: QgsVectorTileLayer, renderer: QgsVectorTileBasicRenderer
) -> None:
    """
    Refreshes a given layer.
    """

    layer.setRenderer(renderer.clone())
    layer.setBlendMode(layer.blendMode())
    layer.setOpacity(layer.opacity())


def get_groups(project: Optional[QgsProject] = None) -> list[QgsLayerTreeNode]:
    instance = project or QgsProject.instance()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None

    return root.children()


def filter_layers(
    layers_to_turn_on: set[str], instance_to_filter: Optional[QgsProject] = None
) -> None:
    """
    Given a set of layers, shows only those layers while hiding others.

    :param layers_to_turn_on: Set of layers to be shown
    :param instance_to_filter: Instance of a QGISProject to filter on.
        If none is provided, the current QGIS project is used instead.
    """

    for child in get_groups(project=instance_to_filter):
        if not isinstance(child, QgsLayerTreeGroup):
            continue

        for layer in get_layers_from_group(child):
            if not isinstance(layer, QgsVectorTileLayer):
                continue
            renderer = layer.renderer()
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
            refresh_layer(layer, renderer)


def has_layers() -> bool:
    instance = QgsProject.instance()
    assert instance is not None
    layers = instance.mapLayers()
    return bool(layers)


def is_quick_osm_layer(layer: QgsVectorLayer) -> bool:
    """
    Simple filter for identifying which layers are the results of QuickOSM queries.
    """
    variable_names = layer.customProperty("variableNames")
    if variable_names is None:
        return False
    if "quickosm_query" not in variable_names:
        return False
    return True


def has_quick_osm_layers() -> bool:
    """
    Simple check that there is at least one QuickOSM layer.
    """
    for layer in QgsProject.instance().mapLayers().values():
        if isinstance(layer, QgsVectorLayer) and is_quick_osm_layer(layer):
            return True
    return False
