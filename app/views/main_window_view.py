from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QMenu)
from PySide6.QtCore import Qt, Signal, QEvent

class MainWindow(QMainWindow):
    """VIEW - Interface graphique pour la gestion des patients"""
    
    # Signaux pour communiquer avec le Controller
    current_tab_changed = Signal(int)
    menu_action_triggered = Signal(str)
    
    def __init__(self):
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
        self.tabs.currentChanged.connect(self.current_tab_changed.emit)

        # Créer menu pour l'onglet Comptabilité (visuellement identique aux autres onglets)
        self._init_comptabilite_menu()
        self.setCentralWidget(self.tabs)

    def replace_tab(self, index, new_widget, title):
        """Remplacer un onglet existant par une nouvelle vue"""
        # Bloquer les signaux pendant le remplacement pour éviter la boucle infinie
        self.tabs.blockSignals(True)
        self.tabs.removeTab(index)
        self.tabs.insertTab(index, new_widget, title)
        self.tabs.setCurrentIndex(index)
        self.tabs.blockSignals(False)

    def _init_comptabilite_menu(self):
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
            pass

    def eventFilter(self, obj, event):
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
            return False
        return super().eventFilter(obj, event)