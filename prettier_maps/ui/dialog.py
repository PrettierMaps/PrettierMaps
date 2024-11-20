from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout


class MainDialog(QDialog):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle("Main Dialog")
        self.resize(500, 300)

        layout = QVBoxLayout()

        self.text_box = QLineEdit(self)
        self.text_box.setPlaceholderText("Enter prompt")
        self.text_box.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.text_box.setFixedHeight(100)
        layout.addWidget(self.text_box, 0)

        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add to Existing Map", self)
        button_layout.addWidget(self.add_button)

        self.create_button = QPushButton("Create New Map", self)
        button_layout.addWidget(self.create_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
