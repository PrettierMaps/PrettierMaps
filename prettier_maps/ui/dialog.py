from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
)

import json

from qgis.core import QgsProject, QgsVectorTileLayer, QgsLayerTreeGroup, QgsLayerTreeLayer

from prettier_maps.config.layers import POSSIBLE_LAYERS
from prettier_maps.core import filter_layers
from prettier_maps.core.save_osm_layer import save_quick_osm_layers


class MainDialog(QDialog):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.layer_tree: dict[str, QTreeWidgetItem] = {}
        self.layer_checkboxes: dict[str, QCheckBox] = {}
        self.init_ui()
        filter_layers(POSSIBLE_LAYERS)

    def get_font(self) -> QFont:
        return QFont("Arial", 12)

    def init_ui(self) -> None:
        self.setWindowTitle("Prettier Maps")
        self.resize(500, 600)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        instructions = QLabel("Select Layers")
        instructions.setFont(self.get_font())
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(instructions)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setContentsMargins(0, 0, 0, 0)
        scroll.setMaximumHeight(500)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setFont(self.get_font())

        self.populate_layers()

        self.tree_widget.itemChanged.connect(self.on_item_changed)
        scroll.setWidget(self.tree_widget)
        layout.addWidget(scroll)

        save_button = QPushButton("Save Quick OSM Layers")
        save_button.setFont(self.get_font())
        save_button.clicked.connect(self.save_layers_dialog)
        layout.addWidget(save_button)

        close_button = QPushButton("Close")
        close_button.setFont(self.get_font())
        close_button.clicked.connect(self.close_dialog)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def populate_layers(self):
        project = QgsProject.instance()
        root = project.layerTreeRoot()
        
        if not root:
            print("no layers found")
            return
        
        maptiler_group = root.children()[0] if root.children() else None
        maptiler_planet_layer = maptiler_group.children()[0] if maptiler_group.children() else None

        mp_layer = maptiler_planet_layer.layer()
        renderer = mp_layer.renderer()

        if isinstance(maptiler_planet_layer, QgsLayerTreeLayer):

            styles = renderer.styles()
            
            sublayer_parents = {}

            for style in styles:
                label_name = style.styleName()
                associated_layer = style.layerName()

                if associated_layer in POSSIBLE_LAYERS:
                    if associated_layer not in sublayer_parents:
                        parent_item = QTreeWidgetItem(self.tree_widget)
                        parent_item.setText(0, associated_layer)
                        parent_item.setFlags(parent_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        parent_item.setCheckState(0, Qt.Checked)
                        self.layer_checkboxes[associated_layer] = parent_item
                        sublayer_parents[associated_layer] = parent_item

                    parent_item = self.layer_checkboxes[associated_layer]
                    child_item = QTreeWidgetItem(parent_item)
                    child_item.setText(0, label_name)
                    child_item.setFlags(child_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    child_item.setCheckState(0, Qt.Checked)
                    self.layer_checkboxes[f"{associated_layer}:{label_name}"] = child_item


    def get_selected_layers(self) -> set[str]:
        selected_layers = set()
        for i in range(self.tree_widget.topLevelItemCount()):
            layer_item = self.tree_widget.topLevelItem(i)
            if layer_item.checkState(0) == Qt.Checked:
                selected_layers.add(layer_item.text(0))
            for j in range(layer_item.childCount()):
                sublayer_item = layer_item.child(j)
                if sublayer_item.checkState(0) == Qt.Checked:
                    selected_layers.add(f"{layer_item.text(0)}:{sublayer_item.text(0)}")
        return selected_layers

    def on_item_changed(self, item:QTreeWidgetItem, column: int) -> None:
        state = item.checkState(0)

        if item.parent() is None:
            for i in range(item.childCount()):
                item.child(i).setCheckState(0, state)
        else:
            parent = item.parent()
            checked_children = sum(
                parent.child(i).checkState(0) == Qt.Checked for i in range(parent.childCount())
            )
            if checked_children == 0:
                parent.setCheckState(0, Qt.Unchecked)
            elif checked_children == parent.childCount():
                parent.setCheckState(0, Qt.Checked)
            else:
                parent.setCheckState(0, Qt.PartiallyChecked)


    def save_layers_dialog(self) -> None:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dialog.exec_():
            folder_path = dialog.selectedFiles()[0]
            save_quick_osm_layers(folder_path)
            QMessageBox.information(
                self, "Layers Saved", "All OSM layers have been saved successfully."
            )        


    def close_dialog(self) -> None:
        self.close()
