from collections import defaultdict

from qgis.core import (
    QgsLayerTree,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsProject,
    QgsVectorTileBasicRenderer,
    QgsVectorTileBasicRendererStyle,
    QgsVectorTileLayer,
)

instance = QgsProject.instance()
assert instance is not None
root = instance.layerTreeRoot()
assert root is not None


def get_styles_from_vector_tile_layer(
    layer: QgsVectorTileLayer,
) -> list[QgsVectorTileBasicRendererStyle]:
    renderer = layer.renderer()
    if renderer is None:
        return []

    assert isinstance(renderer, QgsVectorTileBasicRenderer)

    styles = renderer.styles()
    return styles  # type: ignore[no-any-return]


def get_layers_from_group(group: QgsLayerTreeGroup) -> list[QgsLayerTreeLayer]:
    return [layer for layer in group.children() if isinstance(layer, QgsLayerTreeLayer)]


GroupName = str
LayerName = str


def iterate_groups_and_layers(root: QgsLayerTree):
    proj = QgsProject().instance()
    assert proj is not None

    for child in root.children():
        if not isinstance(child, QgsLayerTreeGroup):
            continue

        vector_tile_layers = get_layers_from_group(child)
        for layer in vector_tile_layers:
            layer_mapping: dict[GroupName, list[int]] = defaultdict(list)
            map_layer = layer.layer()
            print(f"{layer!r}, {map_layer!r}")
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


iterate_groups_and_layers(root)
