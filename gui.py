import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton
from myOCR_prototype.takeScrShot import SnippingWidget
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from myOCR_prototype.ui_gui import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.splitter.setSizes([1,1])

        self.ui.pushButton.clicked.connect(self.button1Clicked)
        self.ui.pushButton_3.clicked.connect(self.button3Clicked)

        self.snippingWidget = SnippingWidget(app=QApplication.instance())
        self.snippingWidget.onSnippingCompleted = self.onSnippingCompleted

        self._pixmap = None
        self.lay = None

    def resizeImage(self, pixmap):
        lwidth = self.ui.imageLabel.width()
        pwidth = pixmap.width()
        lheight = self.ui.imageLabel.height()
        pheight = pixmap.height()

        wratio = pwidth * 1.0 / lwidth
        hratio = pheight * 1.0 / lheight

        if pwidth > lwidth or pheight > lheight:
            if wratio > hratio:
                lheight = pheight / wratio
            else:
                lwidth = pwidth / hratio

            scaled_pixmap = pixmap.scaled(lwidth, lheight)
            return scaled_pixmap
        else:
            return pixmap

    def onSnippingCompleted(self,frame):
        self.setWindowState(QtCore.Qt.WindowState.WindowActive)

        if frame is None:
            return

        image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format.Format_RGB888)
        # image.save("snapshot.png")
        pixmap = QPixmap.fromImage(image)
        self._pixmap = self.resizeImage(pixmap)

        if self.lay is None:
            self.lay = QtWidgets.QVBoxLayout(self.ui.scrollAreaWidgetContents)

        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.addWidget(self.ui.imageLabel)
        # path = "G:/Data Analytics/Resnsol Face Recognition/a.jpg"
        # pixMap = QtGui.QPixmap(path)
        self.ui.imageLabel.setPixmap(pixmap)
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.imageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)

        # self.ui.graphicsView.setPixmap(self._pixmap)
    def button1Clicked(self):
        dlg = Dialog(self)
        dlg.exec()
    def button3Clicked(self):
        self.setWindowState(QtCore.Qt.WindowState.WindowMinimized)
        self.snippingWidget.start()




class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(627, 400)
        self.pushButton = QtWidgets.QPushButton(parent=Dialog)
        self.pushButton.setGeometry(QtCore.QRect(270, 160, 80, 24))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.pushButtonClicked)

        self.variable = 0
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "OK"))

    def pushButtonClicked(self):
        print(self.variable)
        self.variable += 1

class Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Create an instance of the GUI
        self.ui = Ui_Dialog()
        # Run the .setupUi() method to show the GUI
        self.ui.setupUi(self)
