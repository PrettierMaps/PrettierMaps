from qgis.gui import QgisInterface
from qgis.PyQt.QtGui import QAction, QIcon, QPainter

from .config import LOGO_PATH


class MapGeniePlugin:
    def __init__(self, iface: QgisInterface):
        self.iface = iface

    def initGui(self):
        # TODO: Add icon
        self.action = QAction(
            QIcon(str(LOGO_PATH)), "MapGenie", self.iface.mainWindow()
        )
        self.action.setObjectName("mapGenieAction")
        self.action.setWhatsThis("Configuration for MapGenie")
        self.action.setStatusTip("This is status tip")
        self.action.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&MapGenie", self.action)

        canvas = self.iface.mapCanvas()
        assert canvas is not None
        canvas.renderComplete.connect(self.renderTest)

    def unload(self):
        self.iface.removePluginMenu("&MapGenie", self.action)
        self.iface.removeToolBarIcon(self.action)

        canvas = self.iface.mapCanvas()
        assert canvas is not None
        canvas.renderComplete.disconnect(self.renderTest)

    def run(self):
        print("MapGeniePlugin: run called!")

    def renderTest(self, painter: QPainter):
        print("MapGeniePlugin: renderTest called!")
