from qgis.gui import QgisInterface

from .plugin import MapGeniePlugin


def classFactory(iface: QgisInterface) -> MapGeniePlugin:
    return MapGeniePlugin(iface)
