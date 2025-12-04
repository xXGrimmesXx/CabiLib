from PySide6.QtWidgets import QWidget

from app.views.patient_view import PatientView
from app.controllers.patient_controller import PatientController
from app.model.patient import Patient

from app.model.rendezVous import RendezVous

from app.views.creer_facture_view import creerFactureView
from app.controllers.creer_facture_controller import CreerFactureController
from app.model.facture import Facture

from app.views.suivre_facture_view import SuivreFactureView
from app.controllers.suivre_facture_controller import SuivreFactureController

from app.views.planning_view import PlanningView
from app.controllers.planning_controller import PlanningController

from app.views.type_rdv_view import TypeRDVView
from app.controllers.type_rdv_controller import TypeRDVController
from app.model.typeRDV import TypeRDV

from app.views.comptabilite_view import ComptabiliteView



class MainController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.views = {}
        self.controllers = {}

        
        # Connecter le changement d'onglet
        self.main_window.current_tab_changed.connect(self.on_tab_changed)
        # Menu actions from main window (comptabilité)
        try:
            self.main_window.menu_action_triggered.connect(self.on_menu_action)
        except Exception:
            pass
        
        # Charger le premier onglet
        self.load_tab(0)
    
    def load_tab(self, index):
        """Charger un onglet à la demande"""

        if index in self.views:
            # Prefer calling controller.refresh() when available, otherwise try view.refresh()
            ctrl = self.controllers.get(index)
            if ctrl and hasattr(ctrl, 'refresh'):
                try:
                    ctrl.refresh()
                except Exception:
                    pass
            else:
                view = self.views.get(index)
                if view and hasattr(view, 'refresh'):
                    try:
                        view.refresh()
                    except Exception:
                        pass
            return  # Déjà chargé
        

        if index == 0:  # Patients
            self.current_view = PatientView()
            self.current_controller = PatientController(Patient, self.current_view)
            self.main_window.replace_tab(0, self.current_view, "👤 Patients")
            self.views[0] = self.current_view
            self.controllers[0] = self.current_controller

        elif index == 1:  # Planning
            self.current_view = PlanningView()
            self.current_controller = PlanningController(RendezVous, self.current_view)
            self.main_window.replace_tab(1, self.current_view, "📅 Planning")
            self.views[1] = self.current_view
            self.controllers[1] = self.current_controller

        elif index == 2:  # Suivi Factures (moved left after removing create-facture tab)
            self.current_view = SuivreFactureView()
            self.current_controller = SuivreFactureController(Facture, self.current_view)
            self.main_window.replace_tab(2, self.current_view, "💼 Suivre Factures")
            self.views[2] = self.current_view

        elif index == 3:  # Types de RDV (shifted)
            self.current_view = TypeRDVView()
            self.current_controller = TypeRDVController(TypeRDV, self.current_view)
            self.main_window.replace_tab(3, self.current_view, "🏥 Types de RDV")
            self.views[3] = self.current_view
            self.controllers[3] = self.current_controller

        elif index == 4:  # Comptabilité (container) - shifted index
            self.current_view = ComptabiliteView()
            self.current_controller = None
            self.main_window.replace_tab(4, self.current_view, "💰 Comptabilité ▾")
            self.views[4] = self.current_view
            self.controllers[4] = self.current_controller

        elif index == 5:  # Propriétés (shifted)
            from app.controllers.propriete_controller import ProprieteController
            self.current_controller = ProprieteController()
            self.current_view = self.current_controller.view
            self.main_window.replace_tab(5, self.current_view, "⚙️ Propriétés")
            self.views[5] = self.current_view
            self.controllers[5] = self.current_controller
    
    def on_tab_changed(self, index):
        self.load_tab(index)

    def on_menu_action(self, action_name):
        """Handle menu actions from the Comptabilité dropdown."""
        if action_name == 'creer_facture':
            # Open the create-facture view inside the Comptabilité stacked container
            compta_index = 4
            self.load_tab(compta_index)
            view = creerFactureView()
            # Instantiate controller and keep reference so signals work
            try:
                controller = CreerFactureController(Facture, view)
                self.controllers[compta_index] = controller
            except Exception:
                self.controllers[compta_index] = None
            compta_view = self.views.get(compta_index)
            if hasattr(compta_view, 'set_current_widget'):
                compta_view.set_current_widget(view)
            else:
                self.main_window.replace_tab(compta_index, view, 'Comptabilité')
                self.views[compta_index] = view
            self.main_window.tabs.setCurrentIndex(compta_index)
        elif action_name == 'creer_devis':
            # Ensure the Comptabilité container is loaded
            compta_index = 4
            self.load_tab(compta_index)
            from app.views.creer_devis_view import CreerDevisView
            view = CreerDevisView()
            compta_view = self.views.get(compta_index)
            if hasattr(compta_view, 'set_current_widget'):
                compta_view.set_current_widget(view)
            else:
                # Fallback: replace tab content
                self.main_window.replace_tab(compta_index, view, 'Comptabilité')
                self.views[compta_index] = view
                self.controllers[compta_index] = None
            self.main_window.tabs.setCurrentIndex(compta_index)
        elif action_name == 'statistiques':
            compta_index = 4
            self.load_tab(compta_index)
            from app.views.statistiques_view import StatistiquesView
            view = StatistiquesView()
            compta_view = self.views.get(compta_index)
            if hasattr(compta_view, 'set_current_widget'):
                compta_view.set_current_widget(view)
            else:
                self.main_window.replace_tab(compta_index, view, 'Comptabilité')
                self.views[compta_index] = view
                self.controllers[compta_index] = None
            self.main_window.tabs.setCurrentIndex(compta_index)