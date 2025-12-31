from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QMenu)
from PySide6.QtCore import Qt, Signal, QEvent,QObject
import traceback

class MainWindow(QMainWindow):
    """VIEW - Interface graphique pour la gestion des patients"""
    
    # Signaux pour communiquer avec le Controller
    current_tab_changed: Signal = Signal(str)
    """Signal émis lors du changement d'onglet (clé explicite)."""
    menu_action_triggered: Signal = Signal(str)
    """Signal émis lors d'une action de menu comptabilité."""
    refresh: Signal = Signal()
    """Signal pour rafraîchir la vue principale."""
    
    def __init__(self) -> None:
        """
        Initialise la fenêtre principale de l'application.
        """
        super().__init__()
        self.setWindowTitle("CabiLib - Gestion Cabinet")
        self.setWindowState(Qt.WindowMaximized)
        
        
        # Créer les onglets
        self.tabs = QTabWidget()
        self.tabs.addTab(QWidget(), "👤 Voir mes patients")
        self.tabs.addTab(QWidget(), "📅 Planning")
        self.tabs.addTab(QWidget(), "💼 Suivre mes facture")
        self.tabs.addTab(QWidget(), "🏥 Types de RDV")
        # Comptabilité (onglet avec menu déroulant)
        self.tabs.addTab(QWidget(), "💰 Comptabilité ▾")
        self.tabs.addTab(QWidget(), "⚙️ Propriétés")
        # Map index to key explicite
        self.index_to_key = {
            0: "patients",
            1: "planning",
            2: "suivi_factures",
            3: "types_rdv",
            4: "comptabilite",
            5: "proprietes"
        }
        self.tabs.currentChanged.connect(self._emit_tab_key)
        self.setCentralWidget(self.tabs)
        self._init_comptabilite_menu()

    def _emit_tab_key(self, index: int) -> None:
        """
        Émet le signal de changement d'onglet avec la clé correspondante.
        Args:
            index (int): Index de l'onglet sélectionné.
        """
        key = self.index_to_key.get(index)
        if key:
            self.current_tab_changed.emit(key)

    def replace_tab(self, index: int, new_widget: QWidget) -> None:
        """
        Remplace un onglet existant par un nouveau widget.
        Args:
            index (int): Index de l'onglet à remplacer.
            new_widget (QWidget): Nouveau widget à insérer.
        """
        """Remplacer un onglet existant par une nouvelle vue"""
        # Bloquer les signaux pendant le remplacement pour éviter la boucle infinie
        self.tabs.blockSignals(True)
        text = self.tabs.tabText(index)
        self.tabs.removeTab(index)
        self.tabs.insertTab(index, new_widget, text)
        self.tabs.setCurrentIndex(index)
        self.tabs.blockSignals(False)

    def _init_comptabilite_menu(self) -> None:
        """
        Initialise le menu déroulant pour l'onglet Comptabilité.
        """
        try:
            tab_index = None
            # find the index of the tab titled 'Comptabilité'
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == '💰 Comptabilité ▾':
                    tab_index = i
                    break
            if tab_index is None:
                return

            # Create menu and actions
            menu = QMenu(self)
            action_creer_facture = menu.addAction('Créer facture')
            action_creer_devis = menu.addAction('Créer devis')
            action_statistiques = menu.addAction('Statistiques')

            # Emit a simple string payload when triggered
            action_creer_facture.triggered.connect(lambda: self.menu_action_triggered.emit('creer_facture'))
            action_creer_devis.triggered.connect(lambda: self.menu_action_triggered.emit('creer_devis'))
            action_statistiques.triggered.connect(lambda: self.menu_action_triggered.emit('statistiques'))

            # Keep references and install event filter on the tab bar so the tab keeps the normal look
            self._compta_tab_index = tab_index
            self._compta_menu = menu
            tab_bar = self.tabs.tabBar()
            self._tab_bar = tab_bar
            # Mark the tab visually to suggest a dropdown
            self.tabs.setTabText(tab_index, '💰 Comptabilité ▾')
            tab_bar.installEventFilter(self)
        except Exception:
            # If anything fails, don't break the app; menu is optional
            traceback.print_exc()
            pass

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Filtre d'événements pour afficher le menu Comptabilité au survol de l'onglet.
        Args:
            obj (QObject): Objet sur lequel l'événement est capté.
            event (QEvent): Événement à traiter.
        Returns:
            bool: True si l'événement est traité, False sinon.
        """
        """Event filter on the tab bar to show the comptabilité menu on hover while keeping normal tab visuals."""
        try:
            if obj is getattr(self, '_tab_bar', None):
                # Handle enter/mousemove to show the menu, and leave/mousemove outside to hide it
                et = event.type()
                if et in (QEvent.MouseMove, QEvent.Enter):
                    pos = event.pos()
                    idx = obj.tabAt(pos)
                    if idx == getattr(self, '_compta_tab_index', None):
                        # Show menu if not already visible
                        if hasattr(self, '_compta_menu') and not self._compta_menu.isVisible():
                            rect = obj.tabRect(idx)
                            self._compta_menu.popup(obj.mapToGlobal(rect.bottomLeft()))
                    else:
                        # If moved outside the compta tab, hide the menu if visible
                        if hasattr(self, '_compta_menu') and self._compta_menu.isVisible():
                            self._compta_menu.hide()
                elif et == QEvent.Leave:
                    # Mouse left the tab bar completely -> hide menu
                    if hasattr(self, '_compta_menu') and self._compta_menu.isVisible():
                        self._compta_menu.hide()
                return False
        except Exception:
            traceback.print_exc()
            return False
        return super().eventFilter(obj, event)