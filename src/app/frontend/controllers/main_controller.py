import traceback
from app.frontend.views.patient_view import PatientView
from app.frontend.controllers.patient_controller import PatientController
from app.backend.model.patient import Patient

from app.backend.model.rendezVous import RendezVous

from app.frontend.views.creer_facture_view import creerFactureView
from app.frontend.controllers.creer_facture_controller import CreerFactureController
from app.backend.model.facture import Facture

from app.frontend.views.suivre_facture_view import SuivreFactureView
from app.frontend.controllers.suivre_facture_controller import SuivreFactureController

from app.frontend.views.planning_view import PlanningView
from app.frontend.controllers.planning_controller import PlanningController

from app.frontend.views.type_rdv_view import TypeRDVView
from app.frontend.controllers.type_rdv_controller import TypeRDVController
from app.backend.model.typeRDV import TypeRDV

from app.frontend.views.comptabilite_view import ComptabiliteView

from app.frontend.views.redevance_view import RedevanceView
from app.frontend.controllers.redevance_controller import RedevanceController

from app.frontend.views.statistiques_view import StatistiquesView
from app.frontend.controllers.statistiques_controller import StatistiquesController

from app.frontend.views.main_window_view import MainWindow



class MainController:
    def __init__(self, main_window: MainWindow):
        self.main_window = main_window
        self.views = {}
        self.controllers = {}

        
        # Connecter le changement d'onglet
        self.main_window.current_tab_changed.connect(self.on_tab_changed)
        # Menu actions from main window (comptabilité)
        try:
            self.main_window.menu_action_triggered.connect(self.on_menu_action)
        except Exception:
            traceback.print_exc()
            pass
        
        # Charger le premier onglet
        self.load_tab("patients")
    
    def load_tab(self, key: str):
        """Charger un onglet à la demande"""
        
        # Map des clés vers les index fixes des onglets
        key_to_index = {
            "patients": 0,
            "planning": 1,
            "suivi_factures": 2,
            "types_rdv": 3,
            "comptabilite": 4,
            "redevance": 5,
            "proprietes": 6
        }

        if key in self.views and key in self.controllers:
            ctrl = self.controllers.get(key)
            # Ne pas appeler on_refresh si le contrôleur est None (ex : comptabilité)
            if ctrl is not None and hasattr(ctrl, 'view') and hasattr(ctrl.view, 'on_refresh'):
                ctrl.view.on_refresh()
            # Utiliser l'index fixe au lieu de calculer depuis le dictionnaire
            tab_index = key_to_index.get(key, 0)
            self.main_window.replace_tab(tab_index, self.views[key])
            return


        if key == "patients":
            self.current_view = PatientView()
            self.current_controller = PatientController(self.current_view)
            self.main_window.replace_tab(0, self.current_view)
            self.views["patients"] = self.current_view
            self.controllers["patients"] = self.current_controller

        elif key == "planning":
            self.current_view = PlanningView()
            self.current_controller = PlanningController(self.current_view)
            self.main_window.replace_tab(1, self.current_view)
            self.views["planning"] = self.current_view
            self.controllers["planning"] = self.current_controller

        elif key == "suivi_factures":
            self.current_view = SuivreFactureView()
            self.current_controller = SuivreFactureController(Facture, self.current_view)
            self.main_window.replace_tab(2, self.current_view)
            self.views["suivi_factures"] = self.current_view
            self.controllers["suivi_factures"] = self.current_controller

        elif key == "types_rdv":
            self.current_view = TypeRDVView()
            self.current_controller = TypeRDVController(self.current_view)
            self.main_window.replace_tab(3, self.current_view)
            self.views["types_rdv"] = self.current_view
            self.controllers["types_rdv"] = self.current_controller

        elif key == "comptabilite":
            self.current_view = ComptabiliteView()
            self.current_controller = None
            self.main_window.replace_tab(4, self.current_view)
            self.views["comptabilite"] = self.current_view
            self.controllers["comptabilite"] = self.current_controller

        elif key == "redevance":
            self.current_view = RedevanceView()
            self.current_controller = RedevanceController(self.current_view)
            self.main_window.replace_tab(5, self.current_view)
            self.views["redevance"] = self.current_view
            self.controllers["redevance"] = self.current_controller


        elif key == "proprietes":
            from app.frontend.controllers.propriete_controller import ProprieteController
            self.current_controller = ProprieteController()
            self.current_view = self.current_controller.view
            self.main_window.replace_tab(6, self.current_view)
            self.views["proprietes"] = self.current_view
            self.controllers["proprietes"] = self.current_controller
    
    def on_tab_changed(self, key:str):
        """Changement d'onglet par clé explicite"""
        self.load_tab(key)

    def on_menu_action(self, action_name: str):
        """Handle menu actions from the Comptabilité dropdown."""
        if action_name == 'creer_facture':
            self.load_tab("comptabilite")
            # Réutilise la vue/contrôleur si déjà créés
            if "facture" not in self.views:
                view = creerFactureView()
                controller = CreerFactureController(Facture, view)
                self.views["facture"] = view
                self.controllers["facture"] = controller
            else:
                view = self.views["facture"]
            compta_view = self.views.get("creer_facture")
            if hasattr(compta_view, 'set_current_widget'):
                compta_view.set_current_widget(view)
            else:
                self.main_window.replace_tab(4, view)
                self.views["creer_facture"] = view
            self.main_window.tabs.setCurrentIndex(4)
        elif action_name == 'creer_devis':
            self.load_tab("comptabilite")
            from app.frontend.views.creer_devis_view import CreerDevisView
            view = CreerDevisView()
            compta_view = self.views.get("creer_devis")
            if hasattr(compta_view, 'set_current_widget'):
                compta_view.set_current_widget(view)
            else:
                self.main_window.replace_tab(4, view)
                self.views["creer_devis"] = view
                self.controllers["creer_devis"] = None
            self.main_window.tabs.setCurrentIndex(4)
        elif action_name == 'statistiques':
            self.load_tab("comptabilite")
            from app.frontend.views.statistiques_view import StatistiquesView
            from app.frontend.controllers.statistiques_controller import StatistiquesController

            if "statistiques" in self.views and "statistiques" in self.controllers:
                controller = self.controllers["statistiques"]
                controller.refresh()
                view = self.views["statistiques"]
            else:
                view = StatistiquesView()
                controller = StatistiquesController(view)
            
            self.main_window.replace_tab(4, view)
            self.views["statistiques"] = view
            self.controllers["statistiques"] = controller
            self.main_window.tabs.setCurrentIndex(4)