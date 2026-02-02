from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtGui import QIcon
from PySide6.QtCore import QRect, Qt

from os import path, environ, makedirs

class IconTopRightDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        self.icon = None
        self.icon_rect = None
        super().__init__(parent)

    def paint(self, painter, option, index):
        # Draw the default item (background, text, etc.)
        super().paint(painter, option, index)
        rect = option.rect
        icon_rect = QRect(
            rect.right() - 18,  # petit décalage pour ne pas couper
            rect.top() + 2,
            16,
            16
        )
        presence = index.data(999)  # Utilisation d'un rôle personnalisé pour la présence
        icon_path = None
        if presence == "A définir":
            icon_path = path.join(environ.get("APPDATA"), "CabiLib/icons", "undefined.png").replace("\\", "/")
        elif presence == "Présent":
            icon_path = path.join(environ.get("APPDATA"), "CabiLib/icons", "present.png").replace("\\", "/")
        elif presence == "Absent":
            icon_path = path.join(environ.get("APPDATA"), "CabiLib/icons", "absent.png").replace("\\", "/")
        elif presence == "Absent excusé":
            icon_path = path.join(environ.get("APPDATA"), "CabiLib/icons", "excused.png").replace("\\", "/")
        if icon_path:
            icon = QIcon(icon_path)
            if not icon.isNull():
                icon.paint(painter, icon_rect, Qt.AlignRight | Qt.AlignTop)

    def sizeHint(self, option, index):
        return super().sizeHint(option, index)
