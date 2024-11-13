from typing import TYPE_CHECKING

from .plugin import PrettierMapsPlugin

if TYPE_CHECKING:
    from qgis.gui import QgisInterface


def classFactory(iface: "QgisInterface") -> PrettierMapsPlugin:
    return PrettierMapsPlugin(iface)
