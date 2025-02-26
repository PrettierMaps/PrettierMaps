from typing import TYPE_CHECKING

from .plugin import PrettierMapsPlugin

if TYPE_CHECKING:
    from qgis.gui import QgisInterface

__version__ = "1.3.0"


def classFactory(iface: "QgisInterface") -> PrettierMapsPlugin:
    return PrettierMapsPlugin(iface)
