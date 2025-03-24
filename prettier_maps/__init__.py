from .interfaces import IQgisInterface
from .plugin import PrettierMapsPlugin

__version__ = "1.4.3"


def classFactory(iface: IQgisInterface) -> PrettierMapsPlugin:
    return PrettierMapsPlugin(iface)  # pragma: no cover
