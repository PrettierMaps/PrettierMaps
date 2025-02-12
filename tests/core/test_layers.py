def test_get_layers_from_group() -> None:
    from qgis.core import QgsLayerTreeGroup, QgsLayerTreeLayer, QgsVectorTileLayer

    group = QgsLayerTreeGroup("test_group")
    v1 = QgsVectorTileLayer(None, "vector_tile_1").id()
    layer1 = QgsLayerTreeLayer(v1, "layer1", )
    v2 = QgsVectorTileLayer(None, "vector_tile_2").id()
    layer2 = QgsLayerTreeLayer(v2, "layer2")
    non_layer = QgsLayerTreeLayer("non_layer")

    group.addChildNode(layer1)
    group.addChildNode(layer2)
    group.addChildNode(non_layer)

    from prettier_maps.core.layers import get_layers_from_group

    result = get_layers_from_group(group)

    assert len(result) == 2
    assert result[0] == layer1.layer()
    assert result[1] == layer2.layer()


def test_filter_layers() -> None:
    from qgis.core import (
        QgsLayerTreeGroup,
        QgsLayerTreeLayer,
        QgsProject,
        QgsVectorTileBasicRenderer,
        QgsVectorTileBasicRendererStyle,
        QgsVectorTileLayer,
    )

    instance = QgsProject()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None

    group = QgsLayerTreeGroup("test_group")
    root.addChildNode(group)

    layer = QgsVectorTileLayer()
    tree_layer = QgsLayerTreeLayer(layer)
    group.addChildNode(tree_layer)

    renderer = QgsVectorTileBasicRenderer()
    style1 = QgsVectorTileBasicRendererStyle()
    style1.setStyleName("water")
    style2 = QgsVectorTileBasicRendererStyle()
    style2.setStyleName("building")
    renderer.setStyles([style1, style2])
    layer.setRenderer(renderer)

    from prettier_maps.core.layers import filter_layers

    filter_layers({"water"}, instance)

    renderer = layer.renderer()
    assert isinstance(renderer, QgsVectorTileBasicRenderer)
    styles = renderer.styles()

    assert styles[0].isEnabled() is True
    assert styles[1].isEnabled() is False
