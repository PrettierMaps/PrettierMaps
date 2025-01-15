from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from prettier_maps.config.layers import POSSIBLE_LAYERS
from prettier_maps.core import filter_layers


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
        self.resize(500, 700)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        instructions = QLabel("Select Layers")

        instructions.setFont(self.get_font())
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(instructions)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setContentsMargins(0, 0, 0, 0)

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

        close_button = QPushButton("Close")
        close_button.setFont(self.get_font())
        close_button.clicked.connect(self.close_dialog)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def get_selected_layers(self) -> set[str]:
        return {
            layer
            for layer, checkbox in self.layer_checkboxes.items()
            if checkbox.isChecked()
        }

    def on_checkbox_changed(self, state: int) -> None:
        selected = self.get_selected_layers()
        filter_layers(selected)

    def close_dialog(self) -> None:
        self.close()
