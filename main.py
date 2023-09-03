import sys
from PyQt6 import QtWidgets, uic
from package import gui

app = QtWidgets.QApplication(sys.argv)
window = gui.MainWindow()
window.show()
app.exec()
