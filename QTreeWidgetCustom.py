from qgis.PyQt import QtCore
from qgis.PyQt.QtWidgets import QTreeWidget

class QTreeWidgetCustom (QTreeWidget):
    keyUp = QtCore.pyqtSignal(int)
    keyDown = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        QTreeWidget.__init__(self, parent)

    def keyPressEvent(self, e):
        key = e.key()
        if key == QtCore.Qt.Key.Key_Up:
            self.keyUp.emit(e.key())
        elif key == QtCore.Qt.Key.Key_Down:
            self.keyDown.emit(e.key())
        elif key == QtCore.Qt.Key.Key_Return:
            self.keyDown.emit(e.key())
        super()
