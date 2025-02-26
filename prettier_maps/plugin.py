from typing import TYPE_CHECKING, Optional

from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtWidgets import QAction

from .config import LOGO_PATH
from .ui import MainDialog

if TYPE_CHECKING:
    from qgis.gui import QgisInterface


class PrettierMapsPlugin:
    def __init__(self, iface: "QgisInterface") -> None:
        self.iface = iface
        self.action: Optional[QAction] = None

    def initGui(self) -> None:
        icon = QIcon(str(LOGO_PATH))

        self.action = QAction(icon, "PrettierMaps", self.iface.mainWindow())
        self.action.setObjectName("prettierMapsAction")
        self.action.setWhatsThis("Configuration for PrettierMaps")
        self.action.setStatusTip("This is status tip")

        self.action.triggered.connect(self.open_dialog)
        self.iface.addWebToolBarIcon(self.action)

    def unload(self) -> None:
        self.iface.removeWebToolBarIcon(self.action)

    def open_dialog(self) -> None:
        dialog = MainDialog(self.iface)
        dialog.exec_()

    def renderTest(self, painter: QPainter) -> None:
        print("PrettierMapsPlugin: renderTest called!")
