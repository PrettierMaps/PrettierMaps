def test_get_layers_from_group():
    from qgis.core import QgsLayerTreeGroup, QgsLayerTreeLayer

    group = QgsLayerTreeGroup("test_group")
    layer1 = QgsLayerTreeLayer(None, "layer1")
    layer2 = QgsLayerTreeLayer(None, "layer2")
    non_layer = QgsLayerTreeGroup("non_layer")

    group.addChildNode(layer1)
    group.addChildNode(layer2)
    group.addChildNode(non_layer)

    from prettier_maps.core.layers import get_layers_from_group

    result = get_layers_from_group(group)

    assert len(result) == 2
    assert result[0] == layer1
    assert result[1] == layer2
