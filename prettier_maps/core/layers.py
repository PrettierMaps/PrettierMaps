from typing import TYPE_CHECKING
from PyQt5.QtGui import QColor

if TYPE_CHECKING:
    from qgis.core import (
        QgsLayerTreeGroup,
        QgsLayerTreeLayer,
        QgsProject,
        QgsVectorTileBasicRenderer,
        QgsVectorTileBasicRendererStyle,
        QgsVectorTileLayer,
    )


def get_layers_from_group(group: "QgsLayerTreeGroup") -> list["QgsLayerTreeLayer"]:
    from qgis.core import QgsLayerTreeLayer

    return [layer for layer in group.children() if isinstance(layer, QgsLayerTreeLayer)]


def refresh_layer(layer: "QgsVectorTileLayer", renderer: "QgsVectorTileBasicRenderer"):
    layer.setRenderer(renderer.clone())
    layer.setBlendMode(layer.blendMode())
    layer.setOpacity(layer.opacity())


def _get_qgis_project() -> "QgsProject | None":
    from qgis.core import QgsProject

    return QgsProject.instance()


def filter_layers(
    layers_to_turn_on: set[str], instance_to_filter: "QgsProject | None" = None
):
    from qgis.core import (
        QgsLayerTreeGroup,
        QgsVectorTileBasicRenderer,
        QgsVectorTileLayer,
    )

    instance = instance_to_filter or _get_qgis_project()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None

    for child in root.children():
        if not isinstance(child, QgsLayerTreeGroup):
            continue

        vector_tile_layers = get_layers_from_group(child)
        for layer in vector_tile_layers:
            map_layer = layer.layer()
            if not isinstance(map_layer, QgsVectorTileLayer):
                continue

            renderer = map_layer.renderer()
            assert renderer is not None

            assert isinstance(renderer, QgsVectorTileBasicRenderer)

            styles = renderer.styles()
            new_styles: list[QgsVectorTileBasicRendererStyle] = []
            for style in styles:
                if style.layerName() in layers_to_turn_on:
                    style.setEnabled(True)
                else:
                    style.setEnabled(False)
                new_styles.append(style)

            renderer.setStyles(new_styles)
            refresh_layer(map_layer, renderer)
            

def apply_style_to_QuickOSM_layers():
    from qgis.core import (
        QgsLayerTreeLayer,
        QgsProject,
    )

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
    symbol_renderer = layer.renderer()
    symbol = symbol_renderer.symbol()
    symbol.setColor(QColor.fromRgb(155, 0, 155))


def update_styled_layer(layer: "QgsVectorLayer"):
    from qgis.utils import iface
    layer.triggerRepaint()
    iface.layerTreeView().refreshLayerSymbology(layer.id())
