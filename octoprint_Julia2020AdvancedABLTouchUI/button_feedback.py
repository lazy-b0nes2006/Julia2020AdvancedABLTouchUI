from PyQt4 import QtGui
from buzzer_feedback import buzzer

OriginalPushButton = QtGui.QPushButton
OriginalToolButton = QtGui.QToolButton


class QPushButtonFeedback(QtGui.QPushButton):
    def mousePressEvent(self, QMouseEvent):
        buzzer.buzz()
        OriginalPushButton.mousePressEvent(self, QMouseEvent)


class QToolButtonFeedback(QtGui.QToolButton):
    def mousePressEvent(self, QMouseEvent):
        buzzer.buzz()
        OriginalToolButton.mousePressEvent(self, QMouseEvent)


QtGui.QToolButton = QToolButtonFeedback
QtGui.QPushButton = QPushButtonFeedback


