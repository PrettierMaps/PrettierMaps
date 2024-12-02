from .interfaces import IQgisInterface
from .plugin import PrettierMapsPlugin


def classFactory(iface: IQgisInterface) -> PrettierMapsPlugin:
    return PrettierMapsPlugin(iface)
