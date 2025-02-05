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
from prettier_maps.core import filter_layers
from prettier_maps.core.save_osm_layer import has_layers, save_quick_osm_layers


class MainDialog(QDialog):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.del_or_hide = False
        self.layer_checkboxes: dict[str, QCheckBox] = {}
        self.init_ui()
        filter_layers(POSSIBLE_LAYERS)

    def get_font(self) -> QFont:
        """Gets the font that this object will use.

        :return: The font
        """

        return QFont("Arial", 12)

    def build_layers_area(self) -> QScrollArea:
        """Creates the scrolling area where the layer checkboxes will be listed

        :return: The created scroll area
        """

        # Create the scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setContentsMargins(0, 0, 0, 0)
        scroll.setMaximumHeight(500)

        # Create the layout for the area
        layer_layout = QVBoxLayout()
        layer_layout.setSpacing(30)
        layer_layout.setContentsMargins(20, 20, 20, 20)

        # Add a checkbox and name to represent each layer
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
        return scroll

    def init_ui(self) -> None:
        """Initializes the UI for this object"""

        self.setWindowTitle("Prettier Maps")
        self.resize(500, 600)

        # Create the layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Add the basic instructions
        instructions = QLabel("Select Layers")
        instructions.setFont(self.get_font())
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(instructions)

        # Add the layer checkboxes
        layout.addWidget(self.build_layers_area())

        # Add the Save Layers button
        file_layout = QHBoxLayout()
        save_button = QPushButton("Save Quick OSM Layers")
        save_button.setFont(self.get_font())
        save_button.clicked.connect(self.save_layers_dialog)
        file_layout.addWidget(save_button)
        layout.addLayout(file_layout)

        # Add the close button
        close_button = QPushButton("Close")
        close_button.setFont(self.get_font())
        close_button.clicked.connect(self.close_dialog)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def save_layers_dialog(self) -> None:
        """Opens up a dialog to ask what directory to save the layers into, and then
        saves the layers there.
        """

        if not has_layers():
            QMessageBox.warning(self, "No Layers", "No layers found to save.")
            return

        # Opens up the dialog
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)

        # Saves the layers in the selected directory
        if dialog.exec_():
            folder_path = dialog.selectedFiles()[0]
            save_quick_osm_layers(folder_path)
            QMessageBox.information(
                self, "Layers Saved", "All OSM layers have been saved successfully."
            )

    def get_selected_layers(self) -> set[str]:
        """Gets the layers whose checkbox is enabled

        :return: A set of the layers names for the layers that are currently checked
        """

        return {
            layer
            for layer, checkbox in self.layer_checkboxes.items()
            if checkbox.isChecked()
        }

    def on_checkbox_changed(self, state: int) -> None:
        """Reapplies the changes whenever a checkbox changes states

        :param state: the new state of the checkbox. Argument is ignored
        """

        selected = self.get_selected_layers()
        filter_layers(selected)

    def close_dialog(self) -> None:
        """Closes the dialog"""

        self.close()
