from PySide6.QtWidgets import QFrame
from PySide6.QtCore import Qt

class Separator(QFrame):
    def __init__(self, orientation=Qt.Horizontal):
        super().__init__()
        if orientation == Qt.Horizontal:
            self.setFrameShape(QFrame.HLine)
        else:
            self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)