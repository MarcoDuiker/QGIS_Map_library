from qgis.PyQt.QtWidgets import QTreeWidget
import qgis.PyQt.QtCore

class QTreeWidgetCustom (QTreeWidget):
    keyUp = qgis.PyQt.QtCore.pyqtSignal(int)
    keyDown = qgis.PyQt.QtCore.pyqtSignal(int)

    def __init__(self, parent):
        QTreeWidget.__init__(self, parent)

    def keyPressEvent(self, e):
        key = e.key()
        if key == qgis.PyQt.QtCore.Qt.Key_Up:
            self.keyUp.emit(e.key())
        elif key == qgis.PyQt.QtCore.Qt.Key_Down:
            self.keyDown.emit(e.key())
        elif key == qgis.PyQt.QtCore.Qt.Key_Return:
            self.keyDown.emit(e.key())
        super()
