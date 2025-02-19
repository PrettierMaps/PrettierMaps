from .interfaces import IQgisInterface
from .plugin import PrettierMapsPlugin

__version__ = "0.2.0"


def classFactory(iface: IQgisInterface) -> PrettierMapsPlugin:
    return PrettierMapsPlugin(iface)
