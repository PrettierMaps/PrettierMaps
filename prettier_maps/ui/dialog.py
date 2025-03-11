from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)
from qgis.core import (
    QgsLayerTreeGroup,
    QgsProject,
    QgsVectorTileBasicRenderer,
    QgsVectorTileLayer,
)

from prettier_maps.config.layers import POSSIBLE_LAYERS
from prettier_maps.core import apply_style_to_quick_osm_layers, filter_layers
from prettier_maps.core.save_osm_layer import save_quick_osm_layers


class MainDialog(QDialog):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.layer_checkboxes: dict[str, QTreeWidgetItem] = {}
        self.init_ui()
        filter_layers(self.get_selected_layers())

    def get_font(self) -> QFont:
        return QFont("Arial", 12)

    def init_ui(self) -> None:
        self.setWindowTitle("Prettier Maps")
        self.resize(500, 600)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        self.add_instructions(layout)
        self.add_scroll(layout)
        self.save_button(layout)
        self.add_style_button(layout)
        self.add_close_button(layout)

        self.setLayout(layout)

    def add_instructions(self, layout: QVBoxLayout) -> None:
        instructions = QLabel("Select Layers")
        instructions.setFont(self.get_font())
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(instructions)

    def add_scroll(self, layout: QVBoxLayout) -> None:
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

    def add_save_button(self, layout: QVBoxLayout) -> None:
        save_button = QPushButton("Save Quick OSM Layers")
        save_button.setFont(self.get_font())
        save_button.clicked.connect(self.save_layers_dialog)
        layout.addWidget(layout)

    def add_style_button(self, layout: QVBoxLayout) -> None:
        style_button = QPushButton("Style QuickOSM Layer", self)
        style_button.setFont(self.get_font())
        style_button.clicked.connect(self.style_QuickOSM_layers)
        layout.addWidget(style_button)

    def add_close_button(self, layout: QVBoxLayout) -> None:
        close_button = QPushButton("Close")
        close_button.setFont(self.get_font())
        close_button.clicked.connect(self.close_dialog)
        layout.addWidget(close_button)

    def get_selected_layers(self) -> set[str]:
        selected_layers = {
            k
            for k, v in self.layer_checkboxes.items()
            if v.checkState(0) == Qt.CheckState.Checked
        }
        return selected_layers

    def on_item_changed(self, item: QTreeWidgetItem) -> None:
        parent = item.parent()
        if parent is not None:
            self.update_parent_check_state(parent)
            return

        filter_layers(self.get_selected_layers())

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

    def style_QuickOSM_layers(self) -> None:
        apply_style_to_quick_osm_layers()
        self.close()

    def close_dialog(self) -> None:
        self.close()

    def no_maptier_layers_found(self):
        all_layers_item = QTreeWidgetItem(self.tree_widget)
        all_layers_item.setText(0, "No MapTiler Layers Found")
        all_layers_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

    def get_vector_tile_layers(self):
        project = QgsProject.instance()
        root = project.layerTreeRoot()

        if not root or not root.children():
            self.no_maptier_layers_found()
            return None

        maptiler_group = next(
            (
                child
                for child in root.children()
                if isinstance(child, QgsLayerTreeGroup)
            ),
            None,
        )

        if not maptiler_group:
            self.no_maptier_layers_found()
            return None

        layer_tree_layers = [layer for layer in maptiler_group.children()]

        vector_tile_layers = [
            layer.layer()
            for layer in layer_tree_layers
            if isinstance(layer.layer(), QgsVectorTileLayer)
        ]

        if not vector_tile_layers:
            self.no_maptier_layers_found()
            return None

        return vector_tile_layers

    def populate_layers(self) -> None:
        vector_tile_layers = self.get_vector_tile_layers()
        if vector_tile_layers is None:
            return

        all_layers_item = QTreeWidgetItem(self.tree_widget)
        all_layers_item.setText(0, "All Layers")
        all_layers_item.setFlags(
            all_layers_item.flags()
            | Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsTristate
        )
        all_layers_item.setExpanded(True)
        all_layers_item.setCheckState(0, Qt.CheckState.Checked)
        self.layer_checkboxes["All Layers"] = all_layers_item

        for layer in vector_tile_layers:
            parent_item = QTreeWidgetItem(all_layers_item)
            parent_item.setText(0, layer.name())
            parent_item.setFlags(
                parent_item.flags()
                | Qt.ItemFlag.ItemIsUserCheckable
                | Qt.ItemFlag.ItemIsTristate
            )
            parent_item.setCheckState(0, Qt.CheckState.Checked)
            self.layer_checkboxes[layer.name()] = parent_item
            renderer = layer.renderer()
            assert isinstance(renderer, QgsVectorTileBasicRenderer)
            styles = renderer.styles()

            sublayer_parents = {}

            for style in styles:
                label_name = style.styleName()
                associated_layer = style.layerName()

                if associated_layer not in POSSIBLE_LAYERS:
                    continue

                if associated_layer not in sublayer_parents:
                    child_item = QTreeWidgetItem(parent_item)
                    child_item.setText(0, associated_layer)
                    child_item.setFlags(
                        child_item.flags()
                        | Qt.ItemFlag.ItemIsUserCheckable
                        | Qt.ItemFlag.ItemIsTristate
                    )
                    child_item.setCheckState(0, Qt.CheckState.Checked)
                    self.layer_checkboxes[associated_layer] = child_item
                    sublayer_parents[associated_layer] = child_item

                child_item = sublayer_parents[associated_layer]

                grandchild_item = QTreeWidgetItem(child_item)
                grandchild_item.setText(0, label_name)
                grandchild_item.setFlags(
                    grandchild_item.flags() | Qt.ItemFlag.ItemIsUserCheckable
                )
                grandchild_item.setCheckState(
                    0,
                    Qt.CheckState.Checked
                    if style.isEnabled()
                    else Qt.CheckState.Unchecked,
                )
                self.layer_checkboxes[label_name] = grandchild_item
        if all_layers_item is not None:
            self.update_parent_check_state(all_layers_item)

    def has_uniform_child_states(self, item: QTreeWidgetItem) -> None:
        children = [
            item.child(i)
            for i in range(item.childCount())
            if isinstance(item.child(i), QTreeWidgetItem)
        ]
        all_checked = all(
            child.checkState(0) == Qt.CheckState.Checked for child in children
        )
        all_unchecked = all(
            child.checkState(0) == Qt.CheckState.Unchecked for child in children
        )
        return all_checked, all_unchecked

    def update_parent_check_state(self, item: QTreeWidgetItem) -> None:
        if item is None:
            return
        if item.childCount() == 0:
            return

        all_checked, all_unchecked = self.has_uniform_child_states(item)

        if all_checked:
            item.setCheckState(0, Qt.CheckState.Checked)
        elif all_unchecked:
            item.setCheckState(0, Qt.CheckState.Unchecked)
        else:
            item.setCheckState(0, Qt.CheckState.PartiallyChecked)

        # Recursively update parent items
        parent = item.parent()
        if parent is not None:
            self.update_parent_check_state(parent)
