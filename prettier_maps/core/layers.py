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


def iterate_groups_and_layers(
    root: QgsLayerTree,
):
    for child in root.children():
        if not isinstance(child, QgsLayerTreeGroup):
            continue

        layer_mapping: dict[
            GroupName, list[tuple[LayerName, QgsVectorTileBasicRendererStyle]]
        ] = defaultdict(list)

        vector_tile_layers = get_layers_from_group(child)
        for layer in vector_tile_layers:
            map_layer = layer.layer()
            print(f"{layer!r}, {map_layer!r}")
            if not isinstance(map_layer, QgsVectorTileLayer):
                continue

            styles = get_styles_from_vector_tile_layer(map_layer)

            for style in styles:
                symbol = style.symbol()
                if symbol is None:
                    continue
                layer_mapping[style.layerName()].append((style.styleName(), style))

        for new_group_name, styles in layer_mapping.items():
            new_group = child.addGroup(new_group_name)
            assert new_group is not None
            for layer_name, style in styles:
                new_layer = QgsVectorTileLayer(baseName=layer_name)
                tree_layer = QgsLayerTreeLayer(new_layer)
                renderer = QgsVectorTileBasicRenderer()
                style_copy = QgsVectorTileBasicRendererStyle(style)
                renderer.setStyles([style_copy])
                new_layer.setRenderer(renderer)
                new_group.addChildNode(tree_layer)
                new_layer.triggerRepaint()


iterate_groups_and_layers(root)
