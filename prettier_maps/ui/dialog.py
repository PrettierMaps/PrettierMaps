from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from prettier_maps.config.layers import POSSIBLE_LAYERS
from prettier_maps.core import apply_style_to_quick_osm_layers, filter_layers
from prettier_maps.core.save_osm_layer import save_quick_osm_layers


class MainDialog(QDialog):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.del_or_hide = False
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

        # Add the "Select All" checkbox
        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.setFont(self.get_font())
        self.select_all_checkbox.setChecked(True)  # Initially checked
        self.select_all_checkbox.stateChanged.connect(self.select_all_changed)
        layout.addWidget(self.select_all_checkbox)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setContentsMargins(0, 0, 0, 0)
        scroll.setMaximumHeight(500)

        layer_layout = QVBoxLayout()
        layer_layout.setSpacing(30)
        layer_layout.setContentsMargins(20, 20, 20, 20)

        for layer in sorted(POSSIBLE_LAYERS):
            checkbox = QCheckBox(layer.title())
            checkbox.setFont(self.get_font())
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.on_checkbox_changed)
            self.layer_checkboxes[layer] = checkbox
            layer_layout.addWidget(checkbox)

        scroll_widget = QWidget()
        scroll_widget.setLayout(layer_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # File layout for save button
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

    def add_style_button(self, layout: QVBoxLayout):
        style_button = QPushButton("Style QuickOSM Layer", self)
        style_button.setFont(self.get_font())
        style_button.clicked.connect(self.style_QuickOSM_layers)
        layout.addWidget(style_button)

    def get_selected_layers(self) -> set[str]:
        return {
            layer
            for layer, checkbox in self.layer_checkboxes.items()
            if checkbox.isChecked()
        }

    def style_QuickOSM_layers(self) -> None:
        apply_style_to_quick_osm_layers()
        self.close()

    def on_checkbox_changed(self, state: int) -> None:
        selected = self.get_selected_layers()
        filter_layers(selected)
        all_checked = all(
            checkbox.isChecked() for checkbox in self.layer_checkboxes.values()
        )

        self.select_all_checkbox.blockSignals(True)
        self.select_all_checkbox.setChecked(all_checked)
        self.select_all_checkbox.blockSignals(False)

    def select_all_changed(self, state: int) -> None:
        new_state = state == Qt.CheckState.Checked

        # Update all layer checkboxes
        for checkbox in self.layer_checkboxes.values():
            checkbox.setChecked(new_state)

        # Update the filtered layers
        selected = self.get_selected_layers()
        filter_layers(selected)

    def close_dialog(self) -> None:
        self.close()
