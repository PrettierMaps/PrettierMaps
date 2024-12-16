from abc import abstractmethod
from typing import Union

from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction, QWidget


class IQgisInterface(QObject):  # type: ignore[misc]
    @abstractmethod
    def mainWindow(self) -> Union[QWidget, None]: ...
    @abstractmethod
    def addWebToolBarIcon(self, qAction: Union[QAction, None]) -> int: ...  # noqa: N803
    @abstractmethod
    def removeWebToolBarIcon(self, qAction: Union[QAction, None]) -> None: ...  # noqa: N803
