import tempfile
from pathlib import Path
from typing import List

from qgis.core import (
    Qgis,
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsMapLayer,
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
)
from prettier_maps.core.save_osm_layer import save_quick_osm_layers
from prettier_maps.core.style_osm_layer import style_single_layer


def test_get_layers_from_group_with_empty_group() -> None:
    group = QgsLayerTreeGroup("empty_group")
    result = get_layers_from_group(group)
    assert result == []


def test_get_layers_from_group() -> None:
    group = QgsLayerTreeGroup("test_group")

    # Create valid QgsVectorTileLayer objects
    v1 = QgsVectorTileLayer(
        "type=xyz&url=http://tile.stamen.com/toner/{z}/{x}/{y}.png",
        "vector_tile_1",
    )
    v2 = QgsVectorTileLayer(
        "type=xyz&url=http://tile.stamen.com/toner/{z}/{x}/{y}.png",
        "vector_tile_2",
    )

    # Create QgsLayerTreeLayer objects with valid QgsVectorTileLayer objects
    layer1 = QgsLayerTreeLayer(v1)
    layer2 = QgsLayerTreeLayer(v2)
    non_layer = QgsLayerTreeLayer(QgsVectorLayer("Point?crs=EPSG:4326"))

    group.addChildNode(layer1)
    group.addChildNode(layer2)
    group.addChildNode(non_layer)
    result = get_layers_from_group(group)
    assert len(result) == 2
    assert result[0] == layer1.layer()
    assert result[1] == layer2.layer()


def test_get_layers_from_group_with_only_non_vector_tile_layers() -> None:
    group = QgsLayerTreeGroup("non_vector_tile_group")

    non_layer1 = QgsLayerTreeLayer(
        QgsVectorLayer("Point?crs=EPSG:4326", "non_vector_tile_layer_1", "memory")
    )
    non_layer2 = QgsLayerTreeLayer(
        QgsVectorLayer("LineString?crs=EPSG:4326", "non_vector_tile_layer_2", "memory")
    )

    group.addChildNode(non_layer1)
    group.addChildNode(non_layer2)

    result = get_layers_from_group(group)
    assert result == []


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
    for geom_type in [Qgis.GeometryType(i) for i in range(3)]:
        current_geom_type = ["point", "line", "polygon"][geom_type]
        layer = QgsVectorLayer(
            f"{current_geom_type}?crs=EPSG:4326",
            f"{current_geom_type}_layer",
            "memory",
        )
        symbol = QgsSymbol.defaultSymbol(geom_type)
        renderer = QgsSingleSymbolRenderer(symbol)
        layer.setRenderer(renderer)

        layers.append(layer)
        for layer in layers:
            style_single_layer(layer)

        colors = [layer.renderer().symbol().color() for layer in layers]

        assert all_elements_equal(colors) is True


def test_save_quick_osm_layers():
    project = QgsProject.instance()
    project.clear()

    layer1 = QgsVectorLayer("Point?crs=EPSG:4326", "test_layer1", "memory")
    project.addMapLayer(layer1)
    layer2 = QgsVectorLayer("LineString?crs=EPSG:4326", "test_layer2", "memory")
    project.addMapLayer(layer2)

    with tempfile.TemporaryDirectory() as temp_dir:
        save_quick_osm_layers(temp_dir)

        output_file1 = Path(temp_dir) / "test_layer1_point.gpkg"
        output_file2 = Path(temp_dir) / "test_layer2_line.gpkg"
        assert output_file1.exists()
        assert output_file2.exists()

        # Close the layers to release the file handles
        layer1 = None
        layer2 = None

        qml_file1 = Path(temp_dir) / "test_layer1_point.qml"
        qml_file2 = Path(temp_dir) / "test_layer2_line.qml"
        assert not qml_file1.exists()
        assert not qml_file2.exists()

        new_layer1 = QgsProject.instance().mapLayersByName("test_layer1_point")
        new_layer2 = QgsProject.instance().mapLayersByName("test_layer2_line")
        assert len(new_layer1) == 1
        assert len(new_layer2) == 1
        assert new_layer1[0].isValid()
        assert new_layer2[0].isValid()

        # Remove the new layers from the project to release the file handles
        QgsProject.instance().removeMapLayer(new_layer1[0].id())
        QgsProject.instance().removeMapLayer(new_layer2[0].id())

    project.clear()
