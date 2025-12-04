from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget

class ComptabiliteView(QWidget):
    """Container view for Comptabilité: holds multiple sub-pages in a QStackedWidget."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        # default home page
        home = QLabel("Comptabilité — choisissez une action depuis l'onglet")
        home.setWordWrap(True)
        self.stack.addWidget(home)

    def add_or_get_page(self, widget):
        """Add the widget to the stack if not present; return the widget's index."""
        # Identify pages by class name
        cls_name = widget.__class__.__name__
        for i in range(self.stack.count()):
            w = self.stack.widget(i)
            if w.__class__.__name__ == cls_name:
                return i
        # Not found -> add
        return self.stack.addWidget(widget)

    def set_current_widget(self, widget):
        idx = self.add_or_get_page(widget)
        self.stack.setCurrentIndex(idx)

    def go_home(self):
        self.stack.setCurrentIndex(0)
