from abc import abstractmethod

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction, QWidget


class IQgisInterface(QObject):  # type: ignore[misc]
    @abstractmethod
    def mainWindow(self) -> QWidget | None: ...
    @abstractmethod
    def addWebToolBarIcon(self, qAction: QAction | None) -> int: ...  # noqa: N803
    @abstractmethod
    def removeWebToolBarIcon(self, qAction: QAction | None) -> None: ...  # noqa: N803
