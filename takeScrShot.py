import sys

import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from PyQt6 import uic

import numpy as np
import cv2
from PIL import ImageGrab

class SnippingWidget(QWidget):
    is_snipping = False

    def __init__(self, parent=None, app=None):
        super(SnippingWidget, self).__init__()
        self.parent = parent
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.FramelessWindowHint)
        # self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("no title")
        self.screen = app.primaryScreen()
        self.setGeometry(0, 0, self.screen.size().width(), self.screen.size().height())
        self.begin = QPoint()
        self.end = QPoint()
        self.onSnippingCompleted = None

    def fullscreen(self):
        img = ImageGrab.grab(bbox=(0, 0, self.screen.size().width(), self.screen.size().height()))

        try:
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        except:
            img = None

        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(img)

    def start(self):
        SnippingWidget.is_snipping = True
        self.setWindowOpacity(0.2)
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.CursorShape.CrossCursor))
        self.show()

    def paintEvent(self, event):
        if SnippingWidget.is_snipping:
            brush_color = (128, 128, 255, 100)
            lw = 1.5
            opacity = 0.2
        else:
            self.begin = QPoint()
            self.end = QPoint()
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0

        self.setWindowOpacity(opacity)
        qp = QPainter(self)
        qp.setPen(QPen(QColor('red'), lw))
        qp.setBrush(QColor(*brush_color))
        rect = QRect(self.begin, self.end)
        qp.drawRect(rect)

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        SnippingWidget.is_snipping = False
        QApplication.restoreOverrideCursor()
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        self.repaint()
        QApplication.processEvents()
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))

        try:
            # img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            img = np.array(img)
        except:
            img = None

        if self.onSnippingCompleted is not None:
            self.onSnippingCompleted(img)

        self.close()

class MainWindow(QMainWindow):
    useQThread = True

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setAcceptDrops(True)

        self.snippingWidget = SnippingWidget(app=QApplication.instance())
        self.snippingWidget.onSnippingCompleted = self.onSnippingCompleted
        self.ui.pushButton_area.clicked.connect(self.snipArea)
        self.ui.pushButton_full.clicked.connect(self.snipFull)

        self._pixmap = None

    def onSnippingCompleted(self, frame):
        self.setWindowState(Qt.WindowActive)
        if frame is None:
            return

        image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        # self._pixmap = self.resizeImage(pixmap)
        self._pixmap = pixmap
        self.ui.label.setPixmap(self._pixmap)

    def snipArea(self):
        self.setWindowState(Qt.WindowMinimized)
        self.snippingWidget.start()

    def snipFull(self):
        self.setWindowState(Qt.WindowMinimized)
        self.snippingWidget.fullscreen()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        filename = urls[0].toLocalFile()
        self.loadFile(filename)
        self.decodeFile(filename)
        event.acceptProposedAction()

    def resizeImage(self, pixmap):
        lwidth = self.ui.label.width()
        pwidth = pixmap.width()
        lheight = self.ui.label.height()
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

    def showMessageBox(self, title, content):
        msgBox = QMessageBox()
        msgBox.setWindowTitle(title)
        msgBox.setText(content)
        msgBox.exec_()

    def closeEvent(self, event):

        msg = "Close the app?"
        reply = QMessageBox.question(self, 'Message',
                                     msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

