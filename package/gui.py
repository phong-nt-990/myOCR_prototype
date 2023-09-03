import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton
from package.takeScrShot import SnippingWidget
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from package.ui_gui import Ui_MainWindow
from package.model import pytesseractModel
from package.function import toPILImage, removeLineBreak
import time
import threading


class Worker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, image, choice):
        super().__init__()
        self.image = image
        self.choice = choice

    def run(self):
        # Call your time-consuming function here
        if self.choice == "1":
            model = pytesseractModel(toPILImage(self.image), choice="1")
        else:
            model = pytesseractModel(toPILImage(self.image), choice="0")
        result = model.picToString()
        self.finished.emit(result)
    # self.movie.start()
    # self.ui.graphicsView.setPixmap(self._pixmap)
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.image = None

        self.ui.splitter.setSizes([1, 1])

        self.ui.pushButton.clicked.connect(self.button1Clicked)
        self.ui.pushButton_3.clicked.connect(self.button3Clicked)

        self.snippingWidget = SnippingWidget(app=QApplication.instance())
        self.snippingWidget.onSnippingCompleted = self.onSnippingCompleted
        self.defaultWidth = self.width()
        self.ui.scrollArea.setFixedWidth(int(self.defaultWidth / 2) - 15)
        self._pixmap = None
        self.lay = None
        self.ui.imageLabel.setText("Press Snip button to start.")
        self.ui.horizontalSlider.setValue(0)
        self.ui.horizontalSlider.valueChanged.connect(self.scaleImg)
        self.ui.horizontalSlider.setRange(-95, 95)
        self.ui.spinBox.setRange(5, 195)
        self.ui.spinBox.setValue(100)
        self.ui.spinBox.valueChanged.connect(self.spinBoxSignal)
        self.ui.spinBox.setSuffix("%")
        self.ui.fontSizeBox.valueChanged.connect(self.setTextBrowserFontSize)
        self.ui.fontSizeBox.setRange(8, 48)
        self.ui.fontSizeBox.setValue(12)
        self.ui.textBrowser.setText("Nothing to see here. Snip or open the photo to show.")
        self.ui.comboBox.addItem("English")
        self.ui.comboBox.addItem("Vietnamese")
        self.ui.comboBox.setCurrentIndex(0)
        self.movie = QMovie("package/loading.gif")
        self.ui.loadingCircle.setMovie(self.movie)
        self.ui.loadingCircle.setScaledContents(True)
        self.ui.loadingCircle.setFixedSize(25, 25)

        self.originalText = ""
        self.isLineBreak = True
        self.ui.pushButton_2.clicked.connect(self.lineBreakButtonClicked)
        # movie.start()

        # self.ui.progressBar.setStyleSheet(
        #     "QProgressBar {"
        #     "   height: 1px;"  # Change the height to your desired size (e.g., 10px)
        #     "   background-color: red;"
        #     "}"
        # )
        # # self.ui.horizontalLayout.setAlignment(self.ui.pushButton_3, QtCore.Qt.AlignmentFlag.AlignHCenter)
        #
        # # Set the progress bar to "Marquee" mode
        # self.ui.progressBar.setRange(0, 0)  # 0-0 range for marquee mode
        # self.ui.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #
        # # Create a timer to start/stop the marquee animation
        # self.timer = QtCore.QTimer(self)
        # self.timer.timeout.connect(self.toggleMarquee)
        # self.timer.start(10000)  # Start the timer with a 1-second interval

    # def toggleMarquee(self):
    #     value = self.ui.progressBar.value()
    #     if value < 100:
    #         self.ui.progressBar.setValue(value + 1)
    #     else:
    #         self.ui.progressBar.setValue(0)
    def lineBreakButtonClicked(self):
        if self.isLineBreak == True:
            self.isLineBreak = False
            if self.originalText != None:
                self.ui.textBrowser.setText(removeLineBreak(self.originalText))
            self.ui.pushButton_2.setText("Line Break: OFF")
        else:
            self.isLineBreak = True
            if self.originalText != None:
                self.ui.textBrowser.setText(self.originalText)
            self.ui.pushButton_2.setText("Line Break: ON")

    def setTextBrowserFontSize(self, value):
        cursor = self.ui.textBrowser.textCursor()
        font = cursor.charFormat().font()
        font.setPointSize(value)
        # cursor.mergeCharFormat(font)
        self.ui.textBrowser.setFont(font)

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

    def onSnippingCompleted(self, frame):
        self.setWindowState(QtCore.Qt.WindowState.WindowActive)

        if frame is None:
            return

        self.image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format.Format_RGB888)
        # image.save("snapshot.png")
        pixmap = QPixmap.fromImage(self.image)
        self._pixmap = pixmap
        if self.lay is None:
            self.lay = QtWidgets.QVBoxLayout(self.ui.scrollAreaWidgetContents)

        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.addWidget(self.ui.imageLabel)
        # path = "G:/Data Analytics/Resnsol Face Recognition/a.jpg"
        # pixMap = QtGui.QPixmap(path)
        self.ui.imageLabel.setPixmap(pixmap)
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.imageLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.ui.scrollArea.setMinimumWidth(30)
        self.ui.scrollArea.setMaximumWidth(1000)
        self.ui.horizontalSlider.setValue(0)

        self.ui.loadingCircle.setHidden(False)
        self.ui.textBrowser.setText("Processing...")
        self.movie.start()
        # model = Model(toPILImage(self.image))
        # outText = model.picToString()
        # self.ui.textBrowser.setText(outText)




        # result = ["result"]
        # thread = threading.Thread(target=modelStart, args=(self.image, result))
        # thread.start()
        # while thread.is_alive():
        #     pass
        # self.ui.textBrowser.setText(result[0])
        # self.movie.stop()
        #
        if self.ui.comboBox.currentIndex() == 1:
            worker = Worker(self.image, "1")
        else:
            worker = Worker(self.image, "0")
        worker.finished.connect(self.onModelResultReady, QtCore.Qt.ConnectionType.QueuedConnection)
        self.thread = threading.Thread(target=worker.run)
        self.thread.start()

        QCoreApplication.processEvents()
    def onModelResultReady(self, result):
        self.movie.stop()
        self.originalText = result
        if self.isLineBreak == True:
            self.ui.textBrowser.setText(result)
        else:
            self.ui.textBrowser.setText(removeLineBreak(result))
        self.ui.loadingCircle.setHidden(True)

    def button1Clicked(self):
        self.ui.imageLabel.setText("Press Snip button to start.")
        self._pixmap = None
        self.ui.horizontalSlider.setValue(0)
        self.ui.spinBox.setValue(100)
        self.ui.scrollArea.setFixedWidth(int(self.defaultWidth / 2) - 15)
        self.ui.fontSizeBox.setValue(12)
        self.ui.textBrowser.setText("Nothing to see here. Snip or open the photo to show.")
        self.isLineBreak = True
        self.ui.pushButton_2.setText("Line Break: ON")
        self.originalText = ""
        # dlg = Dialog(self)
        # dlg.exec()

    def button3Clicked(self):
        self.setWindowState(QtCore.Qt.WindowState.WindowMinimized)
        self.snippingWidget.start()

    def spinBoxSignal(self, value):
        if self._pixmap is None:
            self.ui.spinBox.setValue(100)
            return
        self.ui.horizontalSlider.setValue(value - 100)

    def scaleImg(self, value):
        if self._pixmap is None:
            self.ui.horizontalSlider.setValue(0)
            return
        scl = float((value + 100) * 0.01)
        # scl = 1.0 * exp
        transform = QTransform().scale(scl, scl)

        scaled_pixmap = self._pixmap.transformed(transform)
        self.ui.imageLabel.setPixmap(scaled_pixmap)
        self.ui.spinBox.setValue(value + 100)

# class Ui_Dialog(object):
#     def setupUi(self, Dialog):
#         Dialog.setObjectName("Dialog")
#         Dialog.resize(627, 400)
#         self.pushButton = QtWidgets.QPushButton(parent=Dialog)
#         self.pushButton.setGeometry(QtCore.QRect(270, 160, 80, 24))
#         self.pushButton.setObjectName("pushButton")
#         self.pushButton.clicked.connect(self.pushButtonClicked)
#         self.variable = 0
#         self.retranslateUi(Dialog)
#         QtCore.QMetaObject.connectSlotsByName(Dialog)
#
#     def retranslateUi(self, Dialog):
#         _translate = QtCore.QCoreApplication.translate
#         Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
#         self.pushButton.setText(_translate("Dialog", "OK"))
#
#     def pushButtonClicked(self):
#         print(self.variable)
#         self.variable += 1
#
#
# class Dialog(QDialog):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.ui = Ui_Dialog()
#         self.ui.setupUi(self)
