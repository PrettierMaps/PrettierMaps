from abc import abstractmethod
from typing import Optional

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction, QWidget


class IQgisInterface(QObject):  # type: ignore[misc]
    @abstractmethod
    def mainWindow(self) -> Optional[QWidget]: ...
    @abstractmethod
    def addWebToolBarIcon(self, qAction: Optional[QAction]) -> int: ...  # noqa: N803
    @abstractmethod
    def removeWebToolBarIcon(self, qAction: Optional[QAction]) -> None: ...  # noqa: N803
