from typing import Protocol

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction, QWidget


class IQgisInterfaceProtocol(Protocol):
    def mainWindow(self) -> QWidget | None: ...
    def addWebToolBarIcon(self, qAction: QAction | None) -> int: ...  # noqa: N803
    def removeWebToolBarIcon(self, qAction: QAction | None) -> None: ...  # noqa: N803


class IQgisInterface(QObject, IQgisInterfaceProtocol): ...  # type: ignore[misc]
