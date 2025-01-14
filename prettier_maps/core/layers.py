from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qgis.core import (
        QgsLayerTreeGroup,
        QgsLayerTreeLayer,
        QgsVectorTileBasicRendererStyle,
        QgsVectorTileLayer,
    )


def get_styles_from_vector_tile_layer(
    layer: "QgsVectorTileLayer",
) -> list["QgsVectorTileBasicRendererStyle"]:
    from qgis.core import QgsVectorTileBasicRenderer

    renderer = layer.renderer()
    if renderer is None:
        return []

    assert isinstance(renderer, QgsVectorTileBasicRenderer)

    styles = renderer.styles()
    return styles  # type: ignore[no-any-return]


def get_layers_from_group(group: "QgsLayerTreeGroup") -> list["QgsLayerTreeLayer"]:
    from qgis.core import QgsLayerTreeLayer

    return [layer for layer in group.children() if isinstance(layer, QgsLayerTreeLayer)]


def iterate_layers_and_split_layers(delete_or_hide_pre_existing_layers: bool):
    from qgis.core import (
        QgsLayerTreeGroup,
        QgsProject,
        QgsVectorTileBasicRenderer,
        QgsVectorTileLayer,
    )

    instance = QgsProject.instance()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None
    proj = QgsProject().instance()
    assert proj is not None

    for child in root.children():
        if not isinstance(child, QgsLayerTreeGroup):
            continue

        vector_tile_layers = get_layers_from_group(child)
        for layer in vector_tile_layers:
            layer_mapping: dict[str, list[int]] = defaultdict(list)
            map_layer = layer.layer()
            if not isinstance(map_layer, QgsVectorTileLayer):
                continue

            styles = get_styles_from_vector_tile_layer(map_layer)

            for i, style in enumerate(styles):
                symbol = style.symbol()
                if symbol is None:
                    continue
                layer_mapping[style.layerName()].append(i)

            for new_group_name, styles in layer_mapping.items():
                new_map_layer = map_layer.clone()
                if new_map_layer is None:
                    continue
                new_map_layer.setName(new_group_name)
                renderer = new_map_layer.renderer()
                if renderer is None:
                    continue

                assert isinstance(renderer, QgsVectorTileBasicRenderer)

                current_styles = renderer.styles()
                renderer.setStyles(
                    [current_styles[style_index] for style_index in styles]
                )

                proj.addMapLayer(new_map_layer, False)
                child.addLayer(new_map_layer)

        for layer in vector_tile_layers:
            if delete_or_hide_pre_existing_layers:
                layer.setItemVisibilityChecked(False)
            else:
                child.removeChildNode(layer)

def apply_style_QuickOSM_layer():
    from qgis.core import (
        QgsLayerTreeGroup,
        QgsProject,
        QgsVectorTileBasicRenderer,
        QgsVectorTileLayer,
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
            print(layer.name(), "invalid")
            continue
        if "quickosm_query" not in variable_names:
            print(layer.name(), "invalid")
            continue
        
        print(layer.name(), "valid")
        symbol_renderer = layer.renderer()
        symbol = symbol_renderer.symbol()
        symbol.setColor(QColor.fromRgb(155,0,155))
        layer.triggerRepaint()
        iface.layerTreeView().refreshLayerSymbology(layer.id())