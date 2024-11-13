import sys

from PyQt5.QtWidgets import QApplication

from prettier_maps.ui import MainDialog

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = MainDialog()
    dialog.exec_()
    sys.exit(0)
