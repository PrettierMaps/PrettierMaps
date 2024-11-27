from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout

from ..core import generate_layers


class MainDialog(QDialog):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def get_font(self) -> QFont:
        return QFont("Arial", 12)

    def init_ui(self) -> None:
        self.setWindowTitle("Main Dialog")
        self.resize(500, 300)

        layout = QVBoxLayout()

        self.text_box = QLineEdit(self)
        self.text_box.setPlaceholderText("Enter prompt")
        self.text_box.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.text_box.setFixedHeight(100)
        self.text_box.setFont(self.get_font())
        layout.addWidget(self.text_box, 0)

        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add to Existing Map", self)
        self.add_button.setFont(self.get_font())
        self.add_button.clicked.connect(self.add_to_existing_map)
        button_layout.addWidget(self.add_button)

        self.create_button = QPushButton("Create New Map", self)
        self.create_button.setFont(self.get_font())
        self.create_button.clicked.connect(self.create_new_map)
        button_layout.addWidget(self.create_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def add_to_existing_map(self) -> None:
        generate_layers(self.text_box.text(), False)

    def create_new_map(self) -> None:
        generate_layers(self.text_box.text(), True)
