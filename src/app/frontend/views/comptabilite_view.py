from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget

class ComptabiliteView(QWidget):
    """Container view for Comptabilité: holds multiple sub-pages in a QStackedWidget."""
    def __init__(self) -> None:
        """
        Initialise la vue container pour la Comptabilité (QStackedWidget).
        """
        super().__init__()
        layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        # default home page
        home = QLabel("Comptabilité — choisissez une action depuis l'onglet")
        home.setWordWrap(True)
        self.stack.addWidget(home)

    def add_or_get_page(self, widget: QWidget) -> int:
        """
        Ajoute le widget à la pile s'il n'est pas déjà présent, sinon retourne son index.
        Args:
            widget (QWidget): Widget à ajouter ou rechercher.
        Returns:
            int: Index du widget dans la pile.
        """
        """Add the widget to the stack if not present; return the widget's index."""
        # Identify pages by class name
        cls_name = widget.__class__.__name__
        for i in range(self.stack.count()):
            w = self.stack.widget(i)
            if w.__class__.__name__ == cls_name:
                return i
        # Not found -> add
        return self.stack.addWidget(widget)

    def set_current_widget(self, widget: QWidget) -> None:
        """
        Définit le widget courant affiché dans la pile.
        Args:
            widget (QWidget): Widget à afficher.
        """
        idx = self.add_or_get_page(widget)
        self.stack.setCurrentIndex(idx)

    def go_home(self) -> None:
        """
        Revient à la page d'accueil de la comptabilité.
        """
        self.stack.setCurrentIndex(0)
