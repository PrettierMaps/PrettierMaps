from PyQt5.QtCore import (
    Qt,
    QSettings,
    )
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
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
    QgsLayerTreeLayer,
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
        self.settings = QSettings("PrettierMaps","LayerSelection")
        self.init_ui()

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

        file_layout = QHBoxLayout()
        save_button = QPushButton("Save Quick OSM Layers")
        save_button.setFont(self.get_font())
        save_button.clicked.connect(self.save_layers_dialog)
        file_layout.addWidget(save_button)
        layout.addLayout(file_layout)

        self.add_style_button(layout)

        close_button = QPushButton("Close")
        close_button.setFont(self.get_font())
        close_button.clicked.connect(self.close_dialog)
        layout.addWidget(close_button)

        self.setLayout(layout)


    def populate_layers(self) -> None:
        project = QgsProject.instance()
        assert project is not None
        root = project.layerTreeRoot()

        if not root:
            raise ValueError("No map open")

        if not root.children():
            raise ValueError("No map open")

        maptiler_group = None
        for child in root.children():
            if isinstance(child, QgsLayerTreeGroup):
                maptiler_group = child
                break
            else:
                maptiler_group = None

        if not maptiler_group:
            raise ValueError("No map open")
            return

        layer_tree_layers = [layer for layer in maptiler_group.children()]

        if not all(isinstance(layer, QgsLayerTreeLayer)
                   for layer in layer_tree_layers):
            raise ValueError("No map open")

        vector_tile_layers = [layer.layer() for layer in layer_tree_layers
                      if isinstance(layer.layer(), QgsVectorTileLayer)]

        assert vector_tile_layers is not None
        for layer in vector_tile_layers:
            assert isinstance(layer, QgsVectorTileLayer)

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

        # all_checked = self.settings.value("All Layers", True, type = bool)
        # all_layers_item.setCheckState(0, Qt.CheckState.Checked if all_checked else Qt.CheckState.Unchecked)

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

            # checked = self.settings.value(layer.name(), True, type=bool)
            # parent_item.setCheckState(0,Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

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

                    # checked = self.settings.value(associated_layer, True, type=bool)
                    # child_item.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

                child_item = sublayer_parents[associated_layer]

                grandchild_item = QTreeWidgetItem(child_item)
                grandchild_item.setText(0, label_name)
                grandchild_item.setFlags(grandchild_item.flags()
                                         | Qt.ItemFlag.ItemIsUserCheckable)
                grandchild_item.setCheckState(0, Qt.CheckState.Checked if style.isEnabled() else Qt.CheckState.Unchecked)
                self.layer_checkboxes[label_name] = grandchild_item

                # checked = self.settings.value(label_name, True, type=bool)
                # grandchild_item.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

        filter_layers(self.get_selected_layers())


    def get_selected_layers(self) -> set[str]:
        selected_layers = {
            k
            for k, v in self.layer_checkboxes.items()
            if v.checkState(0) == Qt.CheckState.Checked
        }
        return selected_layers


    def on_item_changed(self, item: QTreeWidgetItem) -> None:
        if item.parent() is not None:
            return
        self.save_checkbox_states()
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


    def add_style_button(self, layout: QVBoxLayout) -> None:
        style_button = QPushButton("Style QuickOSM Layer", self)
        style_button.setFont(self.get_font())
        style_button.clicked.connect(self.style_QuickOSM_layers)
        layout.addWidget(style_button)


    def style_QuickOSM_layers(self) -> None:
        apply_style_to_quick_osm_layers()
        self.close()


    def close_dialog(self) -> None:
        self.close()

    def save_checkbox_states(self) -> None:
        for name, item in self.layer_checkboxes.items():
            self.settings.setValue(name, item.checkState(0) == Qt.CheckState.Checked)
