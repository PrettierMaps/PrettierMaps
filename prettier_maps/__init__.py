from .interfaces import IQgisInterface
from .plugin import PrettierMapsPlugin

__version__ = "1.3.0"


def classFactory(iface: IQgisInterface) -> PrettierMapsPlugin:
    return PrettierMapsPlugin(iface)  # pragma: no cover
