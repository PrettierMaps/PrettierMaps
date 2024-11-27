from PyQt5.QtGui import QColor
from qgis.core import (
    QgsLayerTree,
    QgsLayerTreeNode,
    QgsProject,
    QgsRenderContext,
    QgsVectorLayer,
    QgsVectorTileBasicRenderer,
    QgsVectorTileLayer,
)

root = QgsProject.instance().layerTreeRoot()
assert root is not None


def process_layer(
    root: QgsLayerTree, layer: QgsVectorLayer | QgsVectorTileLayer | None
):
    """Process a single layer and print its properties"""
    if isinstance(layer, QgsVectorLayer):
        renderer = layer.renderer()
        if renderer:
            symbols = renderer.symbols(QgsRenderContext())
            for symbol in symbols:
                print(f"Layer: {layer.name()}")
                print(f"Symbol: {symbol.dump()}")
    elif isinstance(layer, QgsVectorTileLayer):
        print(f"Vector Tile Layer: {layer.name()}")
        renderer_for_vector_tile_layer: QgsVectorTileBasicRenderer = layer.renderer()
        if renderer_for_vector_tile_layer:
            styles = renderer_for_vector_tile_layer.styles()


def iterate_groups_and_layers(
    root: QgsLayerTree, group: QgsLayerTreeNode | None = None
):
    """Recursively iterate through groups and layers"""
    if group is None:
        group = root
    for child in group.children():
        if child.nodeType() == QgsLayerTreeNode.NodeType.NodeGroup:
            print(f"Group: {child.name()}")
            iterate_groups_and_layers(root, child)
        elif child.nodeType() == QgsLayerTreeNode.NodeType.NodeLayer:
            print(f"Layer: {child.name()}")
            layer = child.layer()
            if layer:
                process_layer(root, layer)


iterate_groups_and_layers(root)


def main_():
    for layer in QgsProject.instance().mapLayers().values():
        if isinstance(layer, QgsVectorTileLayer):
            renderer: QgsVectorTileBasicRenderer = layer.renderer()
            if renderer:
                styles = renderer.styles()
                for idx, style in enumerate(styles):
                    print(f"Style {idx}: {style.layerName()}")
