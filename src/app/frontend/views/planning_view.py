from PySide6.QtWidgets import (QColorDialog, QLineEdit, QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                               QTableWidgetItem, QPushButton, QLabel, QHeaderView,
                               QToolTip, QComboBox, QCompleter,QDateEdit,QTimeEdit,
                               QMessageBox, QCheckBox, QSpinBox)
from PySide6.QtCore import Qt, Signal, QStringListModel, QTime, QSize
from PySide6.QtGui import QColor, QFont, QCursor, QIcon
from app.backend.model.note import Note
from app.frontend.widgetPersonalise.icon_top_right_delegate import IconTopRightDelegate
import traceback
from datetime import datetime, timedelta
from app.backend.model.rendezVous import RendezVous
from app.backend.model.typeRDV import TypeRDV
from app.backend.model.patient import Patient

from app.frontend.widgetPersonalise.separator import Separator
from app.backend.services import constantes_manager
from app.frontend.widgetPersonalise.error_boxes import ExceptionHandler

class PlanningView(QWidget):
    """Vue pour afficher le planning hebdomadaire des rendez-vous"""
    
    # Signaux
    previous_week_clicked: Signal = Signal()
    """Signal émis lors du clic sur la semaine précédente."""
    next_week_clicked: Signal = Signal()
    """Signal émis lors du clic sur la semaine suivante."""
    cell_clicked: Signal = Signal(int, str)
    """Signal émis lors du clic sur une cellule du planning (date, heure)."""
    supprimer_clicked: Signal = Signal(object)
    """Signal émis lors de la demande de suppression d'un rendez-vous."""
    creer_clicked: Signal = Signal(object)
    """Signal émis lors de la création d'un rendez-vous."""
    type_rdv_changed: Signal = Signal(int)
    """Signal émis lors du changement de type de rendez-vous dans le formulaire."""

    refresh: Signal = Signal()
    """Signal pour rafraîchir la vue du planning."""
    
    def __init__(self) -> None:
        """
        Initialise la vue du planning hebdomadaire des rendez-vous.
        """
        super().__init__()
        self.rendezvousedition: bool = True
        self.liste_patients: list[Patient] = []
        self.types_rdv : list[TypeRDV] = []
        self.rdvs_selectionne : list[RendezVous] = []
        self.notes_selectionnee : list[Note] = []
        # Les constantes sont chargées dynamiquement depuis le JSON
        self.init_ui()
    
    def init_ui(self) -> None:
        """
        Crée et configure l'interface utilisateur du planning.
        """
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        # ajout du panel des rdv (creation modification suppression)
        edition_layout = QVBoxLayout()
        self.edition_widget = QWidget()
        self.edition_widget.setLayout(edition_layout)
        self.edition_widget.hide()
        self.edition_widget.setMaximumWidth(300)

        main_layout.addWidget(self.edition_widget)

        header_layout = QHBoxLayout()
        edition_layout.addLayout(header_layout)

        self.close_rdv_panel_btn = QPushButton("✖")
        header_layout.addWidget(self.close_rdv_panel_btn)


        self.close_rdv_panel_btn.clicked.connect(self.hide_rdv_onglet)
        self.close_rdv_panel_btn.setMaximumWidth(30)

        self.changeTypeEdition_btn = QPushButton("Rendez-vous")
        header_layout.addWidget(self.changeTypeEdition_btn)
        self.changeTypeEdition_btn.clicked.connect(self.change_type_edition)

        self.close_rdv_panel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.close_rdv_panel_btn.setStyleSheet("QPushButton { border: none; font-size: 16px; } QPushButton:hover { color: red; }")
        

        rdv_panel_layout = QVBoxLayout()
        self.rdv_panel_widget = QWidget()
        self.rdv_panel_widget.setLayout(rdv_panel_layout)
        edition_layout.addWidget(self.rdv_panel_widget)

        self.init_rdv_edition_widget(rdv_panel_layout)

        note_panel_layout = QVBoxLayout()
        self.note_panel_widget = QWidget()
        self.note_panel_widget.hide()
        self.note_panel_widget.setLayout(note_panel_layout)
        edition_layout.addWidget(self.note_panel_widget)

        self.init_note_edition_widget(note_panel_layout)

        edition_layout.addWidget(Separator(Qt.Horizontal))






        repetition_prime_layout = QVBoxLayout()
        repetition_widget = QWidget()
        repetition_widget.setLayout(repetition_prime_layout)
        edition_layout.addWidget(repetition_widget)

        
        #date et heure du rdv
        dateheure_layout = QHBoxLayout()
        repetition_prime_layout.addLayout(dateheure_layout)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDateTime(datetime.now())
        dateheure_layout.addWidget(QLabel("Date:"))
        dateheure_layout.addWidget(self.date_input)

        self.time_input = QTimeEdit()
        heure_fin = constantes_manager.get_constante("HEURE_FIN") or "20:00"
        heure_debut = constantes_manager.get_constante("HEURE_DEBUT") or "08:00"
        # Les heures sont au format "HH:MM"
        h_fin, m_fin = map(int, heure_fin.split(":"))
        h_debut, m_debut = map(int, heure_debut.split(":"))
        self.time_input.setMaximumTime(QTime(h_fin, m_fin))
        self.time_input.setMinimumTime(QTime(h_debut, m_debut))
        self.time_input.setTime(datetime.now().time())
        dateheure_layout.addWidget(QLabel("Heure:"))
        dateheure_layout.addWidget(self.time_input)

        repetition_layout = QVBoxLayout()

        repetition_choix_layout = QHBoxLayout()
        repetition_layout.addLayout(repetition_choix_layout)

        repetition_prime_layout.addLayout(repetition_layout)
        self.repetition_checkbox_input = QCheckBox()
        self.repetition_checkbox_input.setChecked(False)
        self.repetition_checkbox_input.setText("Répéter le rendez-vous")
        repetition_choix_layout.addWidget(self.repetition_checkbox_input)
        
        
        # Fréquence de répétition
        frequence_layout = QHBoxLayout()
        repetition_layout.addLayout(frequence_layout)
        frequence_layout.addWidget(QLabel("Fréquence:"))
        self.frequence_input = QSpinBox()
        self.frequence_input.setMinimum(1)
        self.frequence_input.setMaximum(52)
        self.frequence_input.setValue(1)
        self.frequence_input.setSuffix(" semaine(s)")
        frequence_layout.addWidget(self.frequence_input)
        
        # Date de fin de répétition
        date_fin_repetition_layout = QHBoxLayout()
        repetition_layout.addLayout(date_fin_repetition_layout)
        date_fin_repetition_layout.addWidget(QLabel("Fin de répétition:"))
        self.date_fin_repetition_input = QDateEdit()
        self.date_fin_repetition_input.setCalendarPopup(True)
        self.date_fin_repetition_input.setDateTime(datetime.now() + timedelta(days=30))
        date_fin_repetition_layout.addWidget(self.date_fin_repetition_input)
                


        edition_layout.addWidget(Separator(Qt.Horizontal))


        actions_layout = QHBoxLayout()
        actions_widget = QWidget()
        actions_widget.setLayout(actions_layout)
        edition_layout.addWidget(actions_widget)
        actions_widget.setMaximumHeight(50)

        self.clear_btn = QPushButton("Effacer")
        self.clear_btn.clicked.connect(self.on_clear_clicked)

        self.creer_btn = QPushButton("Créer / Modifier")
        self.creer_btn.clicked.connect(self.on_creer_clicked)

        self.supprimer_btn = QPushButton("Supprimer")
        self.supprimer_btn.clicked.connect(self.on_supprimer_clicked)

        actions_layout.addWidget(self.clear_btn)
        actions_layout.addWidget(self.creer_btn)
        actions_layout.addWidget(self.supprimer_btn)


        # ajout du planning
        planning_layout = QVBoxLayout()
        main_layout.addLayout(planning_layout)
        
        # En-tête avec navigation
        header_layout = QHBoxLayout()
        self.btn_previous = QPushButton("◀ Semaine précédente")
        self.btn_previous.clicked.connect(self.previous_week_clicked.emit)
        
        self.label_week = QLabel()
        self.label_week.setAlignment(Qt.AlignCenter)
        self.label_week.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.btn_next = QPushButton("Semaine suivante ▶")
        self.btn_next.clicked.connect(self.next_week_clicked.emit)
        
        header_layout.addWidget(self.btn_previous)
        header_layout.addWidget(self.label_week, 1)
        header_layout.addWidget(self.btn_next)
        
        planning_layout.addLayout(header_layout)
        
        # Tableau du planning
        self.table = QTableWidget()

        delegate = IconTopRightDelegate()
        self.table.setItemDelegate(delegate)
        
        self.table.setColumnCount(7)  # Heure + 6 jours (Lundi à Samedi)
        self.table.setHorizontalHeaderLabels(["Heure", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"])
        
        # Créneaux horaires de 8h à 20h par tranches de 15 min
        self.time_slots : list[str] = []
        heure_debut = constantes_manager.get_constante("HEURE_DEBUT")or "08:00"
        heure_fin = constantes_manager.get_constante("HEURE_FIN")or "20:00"
        precision = constantes_manager.get_constante("DUREE_CRENNEAU") or 15
        h_debut, m_debut = map(int, heure_debut.split(":"))
        h_fin, m_fin = map(int, heure_fin.split(":"))
        for hour in range(h_debut, h_fin):
            for minute in range(0, 60, precision):
                self.time_slots.append(f"{hour:02d}:{minute:02d}")
        
        self.table.setRowCount(len(self.time_slots))
        
        # Remplir la colonne des heures
        for i, time_slot in enumerate(self.time_slots):
            item = QTableWidgetItem(time_slot)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
            
            item.setTextAlignment(Qt.AlignCenter)
            font = QFont()
            font.setBold(True)
            item.setFont(font)
            self.table.setItem(i, 0, item)
            self.table.setRowHeight(i, 20)  # Hauteur fixe pour chaque ligne
            
        
        # Configurer la table
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QTableWidget.NoSelection)  # Empêche la sélection multiple
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Empêche l'édition
        self.table.cellClicked.connect(self.on_cell_clicked)

        # Activer le tracking de la souris pour les tooltips instantanés
        self.table.setMouseTracking(True)
        self.table.viewport().setMouseTracking(True)
        self.table.cellEntered.connect(self.show_instant_tooltip)

        # Améliorer la lisibilité
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 10px;
                selection-background-color: transparent;
            }
        """)

        # Ajuster la hauteur des lignes pour tenir dans l'écran
        #self.table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        planning_layout.addWidget(self.table)

    def init_rdv_edition_widget(self, rdv_panel_layout):
            
        #id du patient
        patient_titre = QLabel("Gérer un Rendez-vous")
        patient_titre.setAlignment(Qt.AlignCenter)
        patient_titre.setMaximumHeight(25)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        patient_titre.setFont(font)
        rdv_panel_layout.addWidget(patient_titre)
        rdv_panel_layout.addWidget(Separator(Qt.Horizontal))

        idpatient_layout = QHBoxLayout()
        rdv_panel_layout.addLayout(idpatient_layout)
        idpatient_layout.addWidget(QLabel("Patient:"))
        self.patient_input = QComboBox()
        self.patient_input.setEditable(True)
        self.patient_completer = QCompleter()
        self.patient_completer.setCaseSensitivity(Qt.CaseInsensitive)  # Insensible à la casse
        self.patient_completer.setFilterMode(Qt.MatchContains)  # Filtre par contenu (pas seulement début)
        self.patient_input.setCompleter(self.patient_completer)
        idpatient_layout.addWidget(self.patient_input)

        presence_option = constantes_manager.get_constante("PRESENCE_OPTIONS") or []
        self.presence_input = QComboBox()
        self.presence_input.addItems(presence_option)
        self.presence_input.setEditable(True)
        self.presence_completer = QCompleter(presence_option)
        self.presence_completer.setCaseSensitivity(Qt.CaseInsensitive)  # Insensible à la casse
        self.presence_completer.setFilterMode(Qt.MatchContains)  # Filtre par contenu (pas seulement début)
        self.presence_input.setCompleter(self.presence_completer)
        idpatient_layout.addWidget(self.presence_input)

        rdv_panel_layout.addWidget(Separator(Qt.Horizontal))

        #type de RDV
        type_rdv_layout = QHBoxLayout()
        rdv_panel_layout.addLayout(type_rdv_layout)
        type_rdv_layout.addWidget(QLabel("Type RDV :"))
        self.type_rdv_input = QComboBox()
        self.type_rdv_input.setEditable(True)
        self.type_rdv_completer = QCompleter()
        self.type_rdv_completer.setCaseSensitivity(Qt.CaseInsensitive)  # Insensible à la casse
        self.type_rdv_completer.setFilterMode(Qt.MatchContains)  # Filtre par contenu (pas seulement début)
        self.type_rdv_input.setCompleter(self.type_rdv_completer)
        self.type_rdv_input.currentIndexChanged.connect(lambda: self.type_rdv_changed.emit(int(self.type_rdv_input.currentData()) if self.type_rdv_input.currentData() is not None else -1))
        type_rdv_layout.addWidget(self.type_rdv_input)

    def init_note_edition_widget(self, note_panel_layout):
            
        #id du patient
        patient_titre = QLabel("Gérer une Note")
        patient_titre.setAlignment(Qt.AlignCenter)
        patient_titre.setMaximumHeight(25)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        patient_titre.setFont(font)
        note_panel_layout.addWidget(patient_titre)
        note_panel_layout.addWidget(Separator(Qt.Horizontal))

        titre_layout = QHBoxLayout()
        note_panel_layout.addLayout(titre_layout)
        titre_layout.addWidget(QLabel("Titre:"))
        self.titre_input = QLineEdit()
        titre_layout.addWidget(self.titre_input)

        duree_layout = QHBoxLayout()
        note_panel_layout.addLayout(duree_layout)
        duree_layout.addWidget(QLabel("Durée (minutes):"))
        self.duree_input = QSpinBox()
        self.duree_input.setMinimum(0)
        self.duree_input.setMaximum(1440)
        self.duree_input.setValue(30)
        duree_layout.addWidget(self.duree_input)

        description_layout = QHBoxLayout()
        note_panel_layout.addLayout(description_layout)
        description_layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        description_layout.addWidget(self.description_input)

        couleur_layout = QHBoxLayout()
        note_panel_layout.addLayout(couleur_layout)
        note_panel_layout.addWidget(QLabel("Couleur :"))
        self.couleur_input = QPushButton("Choisir couleur")
        self.couleur_input.clicked.connect(self.choose_color)
        self.couleur_preview = QLabel("     ")
        self.couleur_preview.setStyleSheet("border: 1px solid black;")
        note_panel_layout.addWidget(self.couleur_preview)
        note_panel_layout.addWidget(self.couleur_input)

    
    def on_refresh(self):
        """Rafraîchir la vue du planning"""
        presence_options = constantes_manager.get_constante("PRESENCE_OPTIONS") or []
        self.presence_input.clear()
        self.presence_input.addItems(presence_options)
        self.presence_completer.setModel(QStringListModel(presence_options))
        self.refresh.emit()
    
    def on_cell_clicked(self, row: int, col: int):
        """Gérer le clic sur une cellule"""
        if col == 0:  # Colonne des heures, ne rien faire
            return
        
        # Récupérer l'heure et le jour
        day_index = col - 1  # 0=Lundi, 1=Mardi, etc.
        text = self.table.item(row, col).text()
        time_slot = ""
        if text == "":
            time_slot = self.time_slots[row]  # Utiliser le créneau horaire de la ligne
            
        else :
            time_slot = self.table.item(row, col).text().split('\n')[0].split('-')[0]  # Extraire l'heure de début via le texte du rdv
        
        # Emettre le signal avec les infos
        self.cell_clicked.emit(day_index, time_slot)
    
    def show_instant_tooltip(self, row, col):
        """Afficher le tooltip instantanément"""
        item = self.table.item(row, col)
        if item and item.toolTip():
            QToolTip.showText(QCursor.pos(), item.toolTip(), self.table)
    
    def set_week_label(self, start_date, end_date):
        """Définir le label de la semaine"""
        try:
            text = f"Semaine du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
            self.label_week.setText(text)
            headers = [
                "Heure",
                "Lundi " + (start_date + timedelta(days=0)).strftime('%d/%m'),
                "Mardi " + (start_date + timedelta(days=1)).strftime('%d/%m'),
                "Mercredi " + (start_date + timedelta(days=2)).strftime('%d/%m'),
                "Jeudi " + (start_date + timedelta(days=3)).strftime('%d/%m'),
                "Vendredi " + (start_date + timedelta(days=4)).strftime('%d/%m'),
                "Samedi " + (start_date + timedelta(days=5)).strftime('%d/%m')
            ]
            if not hasattr(self, 'table') or self.table is None:
                print("[PlanningView] ERREUR: self.table n'existe pas ou est None !")
                return
            if self.table.columnCount() != len(headers):
                print(f"[PlanningView] Correction du nombre de colonnes: table attend {self.table.columnCount()} colonnes, headers={len(headers)}")
                self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
        except Exception as e:
            ExceptionHandler.handle(self,e)
            traceback.print_exc()
    
    def clear_planning(self):
        """Effacer tous les rendez-vous du planning"""
        if not hasattr(self, 'table') or self.table is None:
            return
        for row in range(self.table.rowCount()):
            for col in range(1, self.table.columnCount()):
                try:
                    self.table.setItem(row, col, QTableWidgetItem(""))
                    if (self.table.rowSpan(row, col) > 1 or self.table.columnSpan(row, col) > 1):
                        self.table.setSpan(row, col, 1, 1)  # Reset span
                except Exception as e:
                    print(f"[PlanningView] ERREUR clear_planning: row={row}, col={col}, {e}")
                    ExceptionHandler.handle(self,e)
                    traceback.print_exc()
    
    def add_rdv_to_planning(self,Rdv:RendezVous,patient:Patient,type_rendez_vous:TypeRDV) -> None:
        """
        Ajouter un rendez-vous au planning
        Args:
            Rdv (RendezVous): Objet RendezVous à ajouter au planning.
            patient (Patient): Objet Patient associé au rendez-vous.
            type_rendez_vous (TypeRDV): Objet TypeRDV associé au rendez-vous.
        """
        date = Rdv.date
        jour_index = date.weekday()  # 0=Lundi, 6=Dimanche
        hour = date.hour
        minute = date.minute
        # Arrondir au créneau de 15 min le plus proche
        rounded_minute = (minute // 15) * 15
        time_slot = f"{hour:02d}:{rounded_minute:02d}"
        print(f"DEBUG: Ajout du RDV pour {patient.nom} {patient.prenom} à {time_slot} le jour index {jour_index} date {date}")
        
        # Trouver la ligne correspondant à l'heure
        try:
            row = self.time_slots.index(time_slot)
        except Exception as e:
            ExceptionHandler.handle(self, e)
            return  # Heure non trouvée
        
        col = jour_index + 1  # +1 car colonne 0 = heures
        if (col < 1 or col >= self.table.columnCount()):
            ExceptionHandler.handle(self, ValueError(f"[PlanningView] ERREUR: jour_index {jour_index} hors plage pour les colonnes du planning"))
            return  # Jour hors plage
        
        # Créer le texte du RDV - compact
        rdv_text = f"{date.strftime('%H:%M')}-{(date +type_rendez_vous.duree).strftime('%H:%M')}\n{patient.nom} {patient.prenom}"
        toolTip = f"""
                <b>{patient.nom} {patient.prenom}</b><br>
                {date.strftime('%d/%m/%Y')}<br>
                {date.strftime('%H:%M')} - {(date + type_rendez_vous.duree).strftime('%H:%M')}<br>
                {type_rendez_vous.localisation}<br>
                """
        item = self.add_event_to_planning(rdv_text, toolTip, type_rendez_vous.couleur, type_rendez_vous.duree, row, col)
        item.setData(1000, Rdv)  # Stocker l'objet RendezVous dans la cellule pour référence future
        
        # Stocke le statut de présence dans la data de la cellule (rôle personnalisé)
        item.setData(999, Rdv.presence)  # Stocker le statut de présence dans la cellule

    def add_note_to_planning(self,note:Note) -> None:
        """
        Ajouter un rendez-vous au planning
        Args:
            Rdv (RendezVous): Objet RendezVous à ajouter au planning.
            patient (Patient): Objet Patient associé au rendez-vous.
            type_rendez_vous (TypeRDV): Objet TypeRDV associé au rendez-vous.
        """
        date = note.date
        jour_index = date.weekday()  # 0=Lundi, 6=Dimanche
        hour = date.hour
        minute = date.minute
        # Arrondir au créneau de 15 min le plus proche
        rounded_minute = (minute // 15) * 15
        time_slot = f"{hour:02d}:{rounded_minute:02d}"
        print(f"DEBUG: Ajout de la note {note.titre} à {time_slot} le jour index {jour_index} date {date}")
        
        # Trouver la ligne correspondant à l'heure
        try:
            row = self.time_slots.index(time_slot)
        except Exception as e:
            ExceptionHandler.handle(self, e)
            return  # Heure non trouvée
        
        col = jour_index + 1  # +1 car colonne 0 = heures
        if (col < 1 or col >= self.table.columnCount()):
            ExceptionHandler.handle(self, ValueError(f"[PlanningView] ERREUR: jour_index {jour_index} hors plage pour les colonnes du planning"))
            return  # Jour hors plage
        
        # Créer le texte de la note - compact
        note_text = f"{date.strftime('%H:%M')}-{(date +note.duree).strftime('%H:%M')}\n{note.titre}"
        toolTip = f"""
                <b>{note.titre}</b><br>
                {date.strftime('%d/%m/%Y')}<br>
                {date.strftime('%H:%M')} - {(date + note.duree).strftime('%H:%M')}<br>
                {note.description}<br>
                """
        item = self.add_event_to_planning(note_text, toolTip, note.couleur, note.duree, row, col)
        item.setData(1000, note)  # Stocker l'objet Note dans la cellule pour référence future

        
    def add_event_to_planning(self, rdv_text:str, toolTip:str, color :str, duree:timedelta, row :int, col :int) -> QTableWidgetItem:
        item = QTableWidgetItem(rdv_text)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        item.setTextAlignment(Qt.AlignCenter)
        
        # Police compacte
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        item.setFont(font)

        
        item.setToolTip(toolTip)
        
        item.setBackground(QColor(color))

        if duree > timedelta(minutes=15):
            self.table.setSpan(row, col, max(1, duree.total_seconds() // (15 * 60)), 1)  # Fusionner les cellules selon la durée
        
        
        # Applique le delegate global si ce n'est pas déjà fait
        if not hasattr(self, '_icon_delegate_set'):
            self.table.setItemDelegate(IconTopRightDelegate(self.table))
            self._icon_delegate_set = True

        self.table.setItem(row, col, item)
        return item
    
    def get_current_week_start(self):
        """Retourner la date du lundi de la semaine actuelle"""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday(),hours=today.hour, minutes=today.minute, seconds=today.second, microseconds=today.microsecond)  # Lundi

        return start_of_week
    
    def set_liste_patients(self, patients):
        """Définir la liste des patients pour la recherche"""
        self.liste_patients = patients
        self.patient_input.clear()
        self.patient_input.addItem("")  # Ajouter une entrée vide au début
        for patient in self.liste_patients:
            text_affiche = f"{patient.nom} {patient.prenom}"
            self.patient_input.addItem(text_affiche, patient.id)
        # Utiliser le modèle du QComboBox pour le QCompleter
        self.patient_completer.setModel(self.patient_input.model())
        self.patient_completer.setCompletionRole(Qt.DisplayRole)
        self.patient_completer.activated.connect(self.patient_input.setCurrentIndex)

    def set_liste_type_rdv(self, types_rdv):
        """Définir la liste des types de rendez-vous pour la recherche"""
        self.types_rdv = types_rdv
        self.type_rdv_input.clear()
        self.type_rdv_input.addItem("")  # Ajouter une entrée vide au début
        for i in range(len(self.types_rdv)):
            type_rdv = self.types_rdv[i]
            self.type_rdv_input.addItem(type_rdv.nom, type_rdv.id)
            self.type_rdv_input.setItemData(i+1, QColor(type_rdv.couleur), Qt.BackgroundRole)  # +1 pour l'entrée vide au début

        # Utiliser le modèle du QComboBox pour le QCompleter
        self.type_rdv_completer.setModel(self.type_rdv_input.model())
        self.type_rdv_completer.setCompletionRole(Qt.DisplayRole)
        self.type_rdv_completer.activated.connect(self.type_rdv_input.setCurrentIndex)

    def afficher_details_event(self):
        """Afficher les détails du rendez-vous dans le panneau"""
        if (not (self.rdvs_selectionne and self.notes_selectionnee)) or (len(self.rdvs_selectionne) == 0 and len(self.notes_selectionnee) == 0):
            print("DEBUG: Aucun rendez-vous ou note sélectionné pour afficher les détails.")
            print(f"DEBUG: rdvs_selectionne={self.rdvs_selectionne}, notes_selectionnee={self.notes_selectionnee}")
            return
        
        rdv = self.rdvs_selectionne[0] if self.rdvs_selectionne else None
        note = self.notes_selectionnee[0] if self.notes_selectionnee else None
        print(f"DEBUG: Affichage des détails de l'événement: rdv={rdv}, note={note}")
        if rdv is not None:
            # Sélectionner le patient
            if(rdv.patient_id is not None):
                index = self.find_index_by_data(self.patient_input, rdv.patient_id)
                if index != -1:
                    try :
                        self.patient_input.setCurrentIndex(index)
                    except Exception as e:
                        print(f"Error setting patient index: {e}")
                        ExceptionHandler.handle(self,e)
                        traceback.print_exc()
            else:
                self.patient_input.setCurrentIndex(0)  # Aucun

            # Définir la date et l'heure
            if (rdv.date is not None):
                try : 
                    self.date_input.setDate(rdv.date.date())
                    self.time_input.setTime(rdv.date.time())
                except Exception as e:
                    print(f"Error setting date/time: {e}")
                    ExceptionHandler.handle(self,e)
                    traceback.print_exc()
            else :
                self.date_input.setDate(datetime(2000,1,1,0,1,1))

            # Sélectionner le type de RDV
            if (rdv.type_id is not None):
                type_rdv_index = self.find_index_by_data(self.type_rdv_input, rdv.type_id)

                if type_rdv_index != -1:
                    try :
                        self.type_rdv_input.setCurrentIndex(type_rdv_index)
                    except Exception as e:
                        print(f"Error setting type RDV index: {e}")
                        ExceptionHandler.handle(self,e)
                        traceback.print_exc()
            else:
                self.type_rdv_input.setCurrentIndex(0)  # Aucun

            if (rdv.presence is not None):
                try :
                    self.presence_input.setCurrentText(rdv.presence)
                except Exception as e:
                    print(f"Error setting presence: {e}")
                    ExceptionHandler.handle(self,e)
                    traceback.print_exc()
            else:
                self.presence_input.setCurrentIndex(0)  # Aucun
        elif note is not None:
            # Définir le titre, la durée et la description de la note
            try :
                self.titre_input.setText(note.titre)
                self.duree_input.setValue(note.duree_minutes.total_seconds() // 60)  # Convertir en minutes
                self.description_input.setText(note.description)
                self.selected_color = note.couleur
                self.couleur_preview.setStyleSheet(f"background-color: {self.selected_color};")
            except Exception as e:
                print(f"Error setting note details: {e}")
                ExceptionHandler.handle(self,e)
                traceback.print_exc()

    def find_index_by_data(self, combo, value):
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                return i
        return -1  # non trouvé

    def choose_color(self):
        """Ouvrir le sélecteur de couleur"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.couleur_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            self.selected_color = color.name()

    def on_clear_clicked(self):
        """Effacer le formulaire de RDV"""
        self.patient_input.setCurrentIndex(0)
        self.date_input.setDate(datetime.now().date())
        self.time_input.setTime(datetime.now().time())
        self.type_rdv_input.setCurrentIndex(0)
        self.presence_input.setCurrentIndex(0)
        self.titre_input.setText("")
        self.duree_input.setValue(0)
        self.description_input.setText("")
        self.selected_color = "#FFFFFF"
        self.couleur_preview.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid black;")
        self.rdvs_selectionne = []
        self.notes_selectionnee = []

    def on_creer_clicked(self):
        """Gérer le clic sur le bouton Créer / Modifier"""
        if self.rendezvousedition : 
            self.rdvs_selectionne[0].patient_id = int(self.patient_input.currentData()) if self.patient_input.currentData() is not None else None
            date = self.date_input.date()
            time = self.time_input.time()
            self.rdvs_selectionne[0].date = datetime(date.year(), date.month(), date.day(), time.hour(), time.minute(), 0, 0)
            self.rdvs_selectionne[0].type_id = int(self.type_rdv_input.currentData()) if self.type_rdv_input.currentData() is not None else None
            self.rdvs_selectionne[0].presence = self.presence_input.currentText() if self.presence_input.currentText() != "" else None
            rdvs_a_creer = [self.rdvs_selectionne[0]]

            if (self.repetition_checkbox_input.isChecked()):
                frequence = self.frequence_input.value()
                date_fin_repetition = self.date_fin_repetition_input.date()
                current_date = self.rdvs_selectionne[0].date + timedelta(weeks=frequence)
                
                while current_date <= date_fin_repetition:
                    rdv_copy = RendezVous(
                        id=None,
                        motif="",
                        patient_id=self.rdvs_selectionne[0].patient_id,
                        date=current_date,
                        type_id=self.rdvs_selectionne[0].type_id,
                        presence="A définir",
                    )
                    rdvs_a_creer.append(rdv_copy)
                    current_date += timedelta(weeks=frequence)
            self.creer_clicked.emit(rdvs_a_creer)
        else :
            self.notes_selectionnee[0].titre = self.titre_input.text()
            self.notes_selectionnee[0].duree_minutes = minutes=self.duree_input.value()
            self.notes_selectionnee[0].description = self.description_input.toPlainText()
            self.notes_selectionnee[0].couleur = self.selected_color
            date = self.date_input.date()
            time = self.time_input.time()
            self.notes_selectionnee[0].date = datetime(date.year(), date.month(), date.day(), time.hour(), time.minute(), 0, 0)
            rdvs_a_creer = [self.notes_selectionnee[0]]

            if (self.repetition_checkbox_input.isChecked()):
                frequence = self.frequence_input.value()
                date_fin_repetition = self.date_fin_repetition_input.date()
                current_date = self.notes_selectionnee[0].date + timedelta(weeks=frequence)
                
                while current_date <= date_fin_repetition:
                    note_copy = Note(
                        id=None,
                        titre=self.titre_input.text(),
                        description=self.description_input.toPlainText(),
                        couleur=self.selected_color,
                        date=current_date,
                        duree_minutes=self.duree_input.value()
                    )
                    rdvs_a_creer.append(note_copy)
                    current_date += timedelta(weeks=frequence)
            self.creer_clicked.emit(rdvs_a_creer)


    def on_supprimer_clicked(self):
        """Gérer le clic sur le bouton Supprimer"""
        event = self.rdvs_selectionne[0] if self.rdvs_selectionne[0].id is not None else (self.notes_selectionnee[0] if self.notes_selectionnee[0].id is not None else None)
        print(f"DEBUG: Suppression de l'événement: {event}")
        print(f"DEBUG: rdvs_selectionne={self.rdvs_selectionne}, notes_selectionnee={self.notes_selectionnee}")
        self.supprimer_clicked.emit(event)
        self.on_clear_clicked()

    def afficher_creneau_indisponible(self):
        """Afficher un message indiquant que le créneau est indisponible"""
        QMessageBox.warning(self, "Créneau Indisponible", "Le créneau sélectionné est indisponible.")

    def afficher_champs_obligatoires(self):
        """Afficher un message indiquant que des champs obligatoires sont manquants"""
        QMessageBox.warning(self, "Champs Obligatoires", "Veuillez remplir tous les champs obligatoires du rendez-vous.")

    def show_rdv_onglet(self):
        """Affiche l'onglet de gestion des rendez-vous"""
        self.edition_widget.show()
    
    def hide_rdv_onglet(self):
        """Cache l'onglet de gestion des rendez-vous"""
        self.edition_widget.hide()

    def change_type_edition(self):
        """Change le type d'édition entre rendez-vous et notes"""
        self.rendezvousedition = not self.rendezvousedition
        if self.rendezvousedition:
            self.changeTypeEdition_btn.setText("Rendez-vous")
            self.rdv_panel_widget.show()
            self.note_panel_widget.hide()
        else:
            self.changeTypeEdition_btn.setText("Notes")
            self.rdv_panel_widget.hide()
            self.note_panel_widget.show()

    def update_heure_max(self,time:QTime):
        """Met à jour l'heure maximale du sélecteur en fonction de la date sélectionnée"""
        self.time_input.setMaximumTime(time)

    def erreur_suppression_rdv_facture(self):
        """Afficher un message d'erreur lors de la suppression d'un RDV lié à une facture"""
        QMessageBox.critical(self, "Erreur de suppression", "Ce rendez-vous est lié à une facture et ne peut pas être supprimé.")