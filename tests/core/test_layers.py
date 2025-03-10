from qgis.core import (
    Qgis,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsProject,
    QgsSingleSymbolRenderer,
    QgsSymbol,
    QgsVectorLayer,
    QgsVectorTileBasicRenderer,
    QgsVectorTileBasicRendererStyle,
    QgsVectorTileLayer,
)

from prettier_maps.core.layers import (
    filter_layers,
    get_layers_from_group,
    style_single_layer,
)


def test_get_layers_from_group() -> None:
    group = QgsLayerTreeGroup("test_group")
    v1 = QgsVectorTileLayer(None, "vector_tile_1").id()
    layer1 = QgsLayerTreeLayer(
        v1,
        "layer1",
    )
    v2 = QgsVectorTileLayer(None, "vector_tile_2").id()
    layer2 = QgsLayerTreeLayer(v2, "layer2")
    non_layer = QgsLayerTreeLayer("non_layer")

    group.addChildNode(layer1)
    group.addChildNode(layer2)
    group.addChildNode(non_layer)

    result = get_layers_from_group(group)

    assert len(result) == 2
    assert result[0] == layer1.layer()
    assert result[1] == layer2.layer()


def test_filter_layers() -> None:
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

    filter_layers({"water"}, instance)

    renderer = layer.renderer()
    assert isinstance(renderer, QgsVectorTileBasicRenderer)
    styles = renderer.styles()

    assert styles[0].isEnabled() is True
    assert styles[1].isEnabled() is False


def all_elements_equal(iterable) -> bool:
    return iterable.count(iterable[0]) == len(iterable)


def test_single_layer_styling() -> None:
    instance = QgsProject()
    assert instance is not None
    root = instance.layerTreeRoot()
    assert root is not None

    layer_tree = QgsLayerTreeGroup("root")
    root.addChildNode(layer_tree)

    layers = []
    # this just prints the values of the enum
    print(Qgis.GeometryType(0))
    print(Qgis.GeometryType(1))
    print(Qgis.GeometryType(2))
    for geom_type in [Qgis.GeometryType(i) for i in range(3)]:
        # Correct instantiation of layer
        print(geom_type)
        # print(["point", "line", "polygon"][geom_type])
        layer = QgsVectorLayer(
            f"{['point', 'line', 'polygon'][geom_type]}?crs=EPSG:4326",
            f"{['point', 'line', 'polygon'][geom_type]}_layer",
            "memory",
        )
        # assert layer.isValid()
        symbol = QgsSymbol.defaultSymbol(geom_type)
        # print(symbol)
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)

        layers.append(layer)
        for layer in layers:
            style_single_layer(layer)

        colors = [layer.renderer().symbol().color() for layer in layers]

        assert all_elements_equal(colors) is True


test_single_layer_styling()
