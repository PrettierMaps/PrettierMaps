import webbrowser

from PyQt5.QtCore import (
    QSize,
    Qt,
    QTimer,
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
    Qgis,
    QgsLayerTreeGroup,
    QgsProject,
    QgsVectorTileBasicRenderer,
    QgsVectorTileLayer,
)
from qgis.gui import QgsMessageBar

from prettier_maps.config.layers import POSSIBLE_LAYERS
from prettier_maps.core import filter_layers
from prettier_maps.core.quick_osm_utils import has_quick_osm_layers
from prettier_maps.core.save_osm_layer import save_quick_osm_layers
from prettier_maps.core.style_osm_layer import apply_style_to_quick_osm_layers


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

        # Adding QGIS Message Bar
        self.message_bar = QgsMessageBar(self)
        layout.addWidget(self.message_bar)

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
        save_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        save_button.clicked.connect(self.save_layers_dialog)
        file_layout.addWidget(save_button)
        layout.addLayout(file_layout)

        self.add_style_button(layout)

        close_button = QPushButton("Close")
        close_button.setFont(self.get_font())
        close_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        close_button.clicked.connect(self.close_dialog)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def show_message(
        self, text: str, level: str = "success", duration: int = 5000
    ) -> None:
        colors = {
            "success": "green",
            "warning": "orange",
            "error": "red",
        }
        self.message_label.setText(text)
        self.message_label.setStyleSheet(
            f"QLabel {{ color: white; background-color:{colors.get(level, 'blue')};"
            f"padding: 10px; border-radius: 5px; }}"
        )
        self.message_label.show()

        # Hide the message after the duration
        QTimer.singleShot(duration, self.message_label.hide)

    def populate_layers(self) -> None:
        project = QgsProject.instance()
        root = project.layerTreeRoot()

        if not root or not root.children():
            self.message_bar.pushMessage(
                "Error", "No MapTiler Layers Found", level=Qgis.Critical
            )
            return

        maptiler_group = next(
            (
                child
                for child in root.children()
                if isinstance(child, QgsLayerTreeGroup)
            ),
            None,
        )

        if not maptiler_group:
            self.message_bar.pushMessage(
                "Error", "No MapTiler Layers Found", level=Qgis.Critical
            )
            return

        layer_tree_layers = [layer for layer in maptiler_group.children()]

        vector_tile_layers = [
            layer.layer()
            for layer in layer_tree_layers
            if isinstance(layer.layer(), QgsVectorTileLayer)
        ]

        if not vector_tile_layers:
            self.message_bar.pushMessage(
                "Error", "No MapTiler Layers Found", level=Qgis.Critical
            )
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

    def update_parent_check_state(self, item: QTreeWidgetItem) -> None:
        if item is None:
            return
        if item.childCount() == 0:
            return

        all_checked = True
        all_unchecked = True

        for i in range(item.childCount()):
            child = item.child(i)
            if not isinstance(child, QTreeWidgetItem):
                continue
            if child.checkState(0) == Qt.CheckState.Checked:
                all_unchecked = False
            elif child.checkState(0) == Qt.CheckState.Unchecked:
                all_checked = False
            else:
                all_checked = all_unchecked = False

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
        if not self.check_has_QuickOSM_layers():
            return

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dialog.exec_():
            folder_path = dialog.selectedFiles()[0]
            save_quick_osm_layers(folder_path)
            self.message_bar.pushMessage(
                "Success",
                "All OSM layers have been saved successfully.",
                level=Qgis.Success,
                duration=5,
            )

    def add_style_button(self, layout: QVBoxLayout) -> None:
        style_button = QPushButton("Style QuickOSM Layer", self)
        style_button.setFont(self.get_font())
        style_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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
            self.message_bar.pushMessage(
                "Warning",
                "There are no OSM layers in the current project.",
                level=Qgis.Warning,
                duration=5,
            )
            return False
        return True

    def open_browser(self) -> None:
        webbrowser.open("https://prettiermaps.github.io/PrettierMaps/")

    def close_dialog(self) -> None:
        self.close()
