from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qgis.core import (
        QgsLayerTreeGroup,
        QgsLayerTreeLayer,
        QgsVectorTileBasicRenderer,
        QgsVectorTileBasicRendererStyle,
    )


def get_styles_from_vector_tile_layer(
    renderer: "QgsVectorTileBasicRenderer",
) -> list["QgsVectorTileBasicRendererStyle"]:
    styles = renderer.styles()
    return styles  # type: ignore[no-any-return]


def get_layers_from_group(group: "QgsLayerTreeGroup") -> list["QgsLayerTreeLayer"]:
    from qgis.core import QgsLayerTreeLayer

    return [layer for layer in group.children() if isinstance(layer, QgsLayerTreeLayer)]


def filter_layers(layers_to_turn_on: set[str]):
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

            styles = get_styles_from_vector_tile_layer(renderer)
            new_styles: list[QgsVectorTileBasicRendererStyle] = []
            for style in styles:
                if style.layerName() in layers_to_turn_on:
                    style.setEnabled(True)
                else:
                    style.setEnabled(False)
                new_styles.append(style)
            renderer.setStyles(new_styles)
            map_layer.setRenderer(renderer.clone())
            map_layer.setBlendMode(map_layer.blendMode())
            map_layer.setOpacity(map_layer.opacity())
