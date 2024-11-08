from qgis.gui import QgisInterface

from .ui import MapGeniePlugin


def classFactory(iface: QgisInterface) -> MapGeniePlugin:
    return MapGeniePlugin(iface)
