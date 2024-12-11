from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QCheckBox, QDialog, QLabel, QPushButton, QVBoxLayout

from ..core import iterate_layers_and_split_layers


class MainDialog(QDialog):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.del_or_hide = False
        self.init_ui()

    def get_font(self) -> QFont:
        return QFont("Arial", 12)

    def init_ui(self) -> None:
        self.setWindowTitle("Prettier Maps")
        self.resize(400, 100)

        layout = QVBoxLayout()

        instructions = QLabel(
            "How to use:\n"
            "1. Select a Map from Map Tiler\n"
            "2. Click 'Split Layers' below\n"
            "or\n"
            "1. Get a QuickOSM output\n"
            "2. Click 'Style QuickOSM Layer' below"
        )

        instructions.setFont(self.get_font())
        instructions.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(instructions)

        self.checkbox = QCheckBox(
            "Do you want the MapTiler to be hidden? Check this box for yes, or it will "
            "be deleted upon layering."
        )
        self.checkbox.setFont(self.get_font())
        self.checkbox.stateChanged.connect(self.toggle_del_or_hide)
        layout.addWidget(self.checkbox)

        self.split_button = QPushButton("Split Layers", self)
        self.split_button.setFont(self.get_font())
        self.split_button.clicked.connect(self.split_layers)
        layout.addWidget(self.split_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.style_button = QPushButton("Style QuickOSM Layer", self)
        self.style_button.setFont(self.get_font())
        self.style_button.clicked.connect(self.style_QuickOSM_layers)
        layout.addWidget(self.style_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.setLayout(layout)

    def split_layers(self):
        iterate_layers_and_split_layers(self.del_or_hide)
        self.close()

    def style_QuickOSM_layers(self):
        pass

    def toggle_del_or_hide(self, state: int) -> None:
        """Toggle delOrHide based on the checkbox state."""
        self.del_or_hide = state == Qt.CheckState.Checked
        print(f"delOrHide is now: {self.del_or_hide}")
