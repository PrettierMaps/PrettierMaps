from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout

from ..core import iterate_layers_and_split_layers


class MainDialog(QDialog):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def get_font(self) -> QFont:
        return QFont("Arial", 12)

    def init_ui(self) -> None:
        self.setWindowTitle("Prettier Maps")
        self.resize(400, 100)

        layout = QVBoxLayout()

        instructions = QLabel(
            "How to use:\n"
            "1. Select a Map from Map Tiler, then run here to split layers into "
            "manageable sections\n"
            "2. Click 'Split Layers' below"
        )
        instructions.setFont(self.get_font())
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(instructions)

        self.split_button = QPushButton("Split Layers", self)
        self.split_button.setFont(self.get_font())
        self.split_button.clicked.connect(iterate_layers_and_split_layers)
        layout.addWidget(self.split_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setLayout(layout)
