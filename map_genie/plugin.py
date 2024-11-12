from typing import TYPE_CHECKING

from PyQt5.QtGui import QIcon, QPainter
from PyQt5.QtWidgets import QAction

from .config import LOGO_PATH
from .ui import MainDialog

if TYPE_CHECKING:
    from qgis.gui import QgisInterface


class MapGeniePlugin:
    def __init__(self, iface: "QgisInterface"):
        self.iface = iface

        self.action: QAction | None = None

    def initGui(self) -> None:
        # TODO: Add icon
        icon = QIcon(str(LOGO_PATH))

        self.action = QAction(icon, "MapGenie", self.iface.mainWindow())
        self.action.setObjectName("mapGenieAction")
        self.action.setWhatsThis("Configuration for MapGenie")
        self.action.setStatusTip("This is status tip")

        self.action.triggered.connect(self.open_dialog)
        self.iface.addWebToolBarIcon(self.action)

    def unload(self) -> None:
        self.iface.removeWebToolBarIcon(self.action)

    def open_dialog(self) -> None:
        dialog = MainDialog()
        dialog.exec_()

    def renderTest(self, painter: QPainter) -> None:
        print("MapGeniePlugin: renderTest called!")
