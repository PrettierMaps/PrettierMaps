import webbrowser
from typing import List

from PyQt5.QtCore import (
    QSize,
    Qt,
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import (
    QColorDialog,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStyle,
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
from prettier_maps.core import filter_layers
from prettier_maps.core.quick_osm_utils import has_quick_osm_layers
from prettier_maps.core.save_osm_layer import save_quick_osm_layers
from prettier_maps.core.style_osm_layer import apply_style_to_quick_osm_layers


class MainDialog(QDialog):
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
        self.add_save_button(layout)
        self.add_style_button(layout)
        self.add_close_button(layout)

        self.setLayout(layout)

    def add_insturctions_and_info_button(self, layout: QVBoxLayout) -> None:
        instructions = QLabel("Select Layers")
        instructions.setFont(self.get_font())
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)

        info_button = QPushButton()
        info_button.setFont(self.get_font())

        style = self.style()
        if style is not None:
            info_button.setIcon(
                style.standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView)
            )
            info_button.setIconSize(QSize(20, 20))
            info_button.setFixedSize(20, 20)
            info_button.setStyleSheet("""
                QPushButton {
                    border-radius: 10px;  /* Half of 20 to make it a circle */
                    background-color: #0078D7; /* Windows info blue */
                    color: white;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #005A9E;
                }
                QPushButton:pressed {
                    background-color: #004E8C;
                }
            """)

        info_layout = QHBoxLayout()

        info_button.clicked.connect(self.open_browser)
        info_layout.addWidget(instructions, alignment=Qt.AlignmentFlag.AlignLeft)
        info_layout.addWidget(info_button, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(info_layout)

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
        layout.addWidget(save_button)

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
        """
        Update widget tree and the set of layers shown to the user.
        """
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
        """
        Raises a relevant error to the user.
        """
        all_layers_item = QTreeWidgetItem(self.tree_widget)
        all_layers_item.setText(0, "No MapTiler Layers Found")
        all_layers_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

    def get_vector_tile_layers(self) -> List[QgsVectorTileLayer]:
        """
        Find and return the vector tile layers,
        showing the relevant error when there are none.
        """
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

    def make_tree_widget_item(
        self, parent_widget_item: QTreeWidgetItem, name: str
    ) -> QTreeWidgetItem:
        """
        Setup a new tree widge items, including linking to parent in tree.
        """

        child_widget_item = QTreeWidgetItem(parent_widget_item)
        child_widget_item.setText(0, name)
        child_widget_item.setFlags(
            child_widget_item.flags()
            | Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsTristate
        )
        child_widget_item.setCheckState(0, Qt.CheckState.Checked)

        return child_widget_item

    def populate_layers(self) -> None:
        """
        Creates a widget tree for the open maptiler groups and displays it to the user.
        """
        vector_tile_layers = self.get_vector_tile_layers()
        if vector_tile_layers is None:
            return

        all_layers_item = self.make_tree_widget(self.tree_widget, "All layers")
        self.layer_checkboxes["All Layers"] = all_layers_item
        all_layers_item.setExpanded(True)

        for layer in vector_tile_layers:
            parent_item = self.make_tree_widget(all_layers_item, layer.name())
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
                    child_item = self.make_tree_widget(parent_item, associated_layer)
                    sublayer_parents[associated_layer] = child_item

                child_item = sublayer_parents[associated_layer]

                self.layer_checkboxes[label_name] = self.make_tree_widget(
                    child_item, label_name
                )

        if all_layers_item is not None:
            self.update_parent_check_state(all_layers_item)

    def has_uniform_child_states(self, item: QTreeWidgetItem) -> tuple[bool, bool]:
        """
        Indicates whether the parent item should be checked, unchecked or partially
        checked through a pair of booleans.

        :param item: parent item.
        :return: all chlidren are checked, all children are unchecked.
        """
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
        """
        Recurse back up the widget tree, correcting the checkstate of each parent,
        when an update is made to the check state of an item.
        """
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
        if self.check_has_QuickOSM_layers():
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.FileMode.Directory)
            dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
            if dialog.exec_():
                folder_path = dialog.selectedFiles()[0]
                save_quick_osm_layers(folder_path)
                QMessageBox.information(
                    self, "Layers Saved", "All OSM layers have been saved successfully."
                )
        else:
            return

    def add_style_button(self, layout: QVBoxLayout) -> None:
        style_button = QPushButton("Style QuickOSM Layer", self)
        style_button.setFont(self.get_font())
        style_button.clicked.connect(self.style_QuickOSM_layers)
        layout.addWidget(style_button)

    def style_QuickOSM_layers(self) -> None:
        if self.check_has_QuickOSM_layers():
            colour = QColorDialog.getColor()
            apply_style_to_quick_osm_layers(colour)
        else:
            return

    def check_has_QuickOSM_layers(self) -> bool:
        if not has_quick_osm_layers():
            QMessageBox.warning(
                self,
                "No OSM Layers",
                "There are no OSM layers in the current project.",
            )
            return False
        else:
            return True

    def open_browser(self) -> None:
        webbrowser.open("https://prettiermaps.github.io/PrettierMaps/")

    def close_dialog(self) -> None:
        self.close()
