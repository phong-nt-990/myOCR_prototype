import sys
from PyQt6 import QtWidgets, uic
from myOCR_prototype import gui

app = QtWidgets.QApplication(sys.argv)
window = gui.MainWindow()
window.show()
app.exec()
