from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class CreerDevisView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Page de création de devis (placeholder)"))
