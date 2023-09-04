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

class SnippingWidget(QtWidgets.QWidget):
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

