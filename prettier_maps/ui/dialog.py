from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout


class MainDialog(QDialog):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle("Main Dialog")
        self.resize(500, 500)

        layout = QVBoxLayout()
        label = QLabel("Hello World", self)
        layout.addWidget(label)
        self.setLayout(layout)
