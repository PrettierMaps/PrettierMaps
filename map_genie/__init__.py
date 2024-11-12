from typing import TYPE_CHECKING

from .plugin import MapGeniePlugin

if TYPE_CHECKING:
    from qgis.gui import QgisInterface


def classFactory(iface: "QgisInterface") -> MapGeniePlugin:
    return MapGeniePlugin(iface)
