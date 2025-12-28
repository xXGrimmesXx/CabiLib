"""
Vue pour la gestion des propriétés du cabinet et du praticien.
Permet la modification des constantes de l'application avec sauvegarde automatique.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem, QFileDialog,
    QGroupBox, QScrollArea, QSpinBox
)
from PySide6.QtCore import Signal, Qt
from app.services import constantes_manager


class ProprieteView(QWidget):
    """
    Vue pour l'édition des propriétés du cabinet/praticien.
    Utilise des signaux Qt pour communiquer avec le contrôleur.
    """
    
    # Signaux pour communication avec le contrôleur
    constante_modified = Signal(str, object)  # (clé, nouvelle_valeur)
    list_item_added = Signal(str, str)  # (clé_liste, nouvelle_valeur)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Propriétés du Cabinet")
        self._init_ui()
        
    def _init_ui(self):
        """Initialise l'interface utilisateur."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Scroll area pour gérer le contenu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Groupe: Informations du praticien
        layout.addWidget(self._create_practitioner_group())
        
        # Groupe: Informations du cabinet
        layout.addWidget(self._create_cabinet_group())
        
        # Groupe: Paramètres administratifs
        layout.addWidget(self._create_admin_group())
        
        # Groupe: Listes d'options
        layout.addWidget(self._create_lists_group())
        
        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
    def _create_practitioner_group(self) -> QGroupBox:
        """Crée le groupe des informations du praticien."""
        group = QGroupBox("Informations du Praticien")
        layout = QVBoxLayout()
        
        # Nom du praticien
        layout.addLayout(self._create_text_field(
            "PRACTITIONER_NAME", 
            "Nom du praticien"
        ))
        
        # Téléphone
        layout.addLayout(self._create_text_field(
            "PRACTITIONER_PHONE", 
            "Téléphone du praticien"
        ))
        
        # Email
        layout.addLayout(self._create_text_field(
            "PRACTITIONER_EMAIL", 
            "Email du praticien"
        ))
        
        group.setLayout(layout)
        return group
        
    def _create_cabinet_group(self) -> QGroupBox:
        """Crée le groupe des informations du cabinet."""
        group = QGroupBox("Informations du Cabinet")
        layout = QVBoxLayout()
        
        # Adresse du cabinet
        layout.addLayout(self._create_text_field(
            "CABINET_ADDRESS", 
            "Adresse du cabinet"
        ))
        
        # Dossier des factures (avec bouton de sélection)
        layout.addLayout(self._create_directory_field(
            "FACTURES_DIR", 
            "Dossier de sauvegarde des factures"
        ))
        
        group.setLayout(layout)
        return group
        
    def _create_admin_group(self) -> QGroupBox:
        """Crée le groupe des paramètres administratifs."""
        group = QGroupBox("Paramètres Administratifs")
        layout = QVBoxLayout()
        
        # Historique d'absence (nombre de jours)
        layout.addLayout(self._create_number_field(
            "HISTORIQUE_ABSENCE_JOURS", 
            "Historique d'absence (jours)",
            min_val=1,
            max_val=365
        ))
        
        # Délai de paiement
        layout.addLayout(self._create_number_field(
            "DELAI_PAIEMENT_FACTURE_DAYS", 
            "Délai de paiement (jours)",
            min_val=1,
            max_val=180
        ))
        
        # SIRET
        layout.addLayout(self._create_text_field(
            "SIRET", 
            "SIRET"
        ))
        
        # APE
        layout.addLayout(self._create_text_field(
            "APE", 
            "Code APE"
        ))
        
        # ADELI
        layout.addLayout(self._create_text_field(
            "ADELI", 
            "Numéro ADELI"
        ))
        
        group.setLayout(layout)
        return group
        
    def _create_lists_group(self) -> QGroupBox:
        """Crée le groupe des listes d'options (en colonnes)."""
        group = QGroupBox("Listes d'Options (Ajout uniquement)")
        main_layout = QVBoxLayout()
        
        # Disposer les listes en colonnes (2x2)
        row1 = QHBoxLayout()
        row1.addWidget(self._create_list_widget(
            "AMENAGEMENTS_OPTIONS",
            "Aménagements"
        ))
        row1.addWidget(self._create_list_widget(
            "NIVEAU_SCOLAIRE_OPTIONS",
            "Niveaux scolaires"
        ))
        
        row2 = QHBoxLayout()
        row2.addWidget(self._create_list_widget(
            "TYPE_TELEPHONE_OPTIONS",
            "Types de téléphone"
        ))
        row2.addWidget(self._create_list_widget(
            "LOCALISATIONS_RDV",
            "Localisations RDV"
        ))
        
        main_layout.addLayout(row1)
        main_layout.addLayout(row2)
        
        group.setLayout(main_layout)
        return group
        
    def _create_text_field(self, key: str, label: str) -> QHBoxLayout:
        """
        Crée un champ texte avec sauvegarde automatique à la perte de focus.
        
        Args:
            key: Clé de la constante
            label: Label à afficher
            
        Returns:
            Layout contenant le label et le champ
        """
        layout = QHBoxLayout()
        layout.addWidget(QLabel(f"{label} :"))
        
        line_edit = QLineEdit()
        value = constantes_manager.get_constante(key)
        line_edit.setText(str(value) if value is not None else "")
        
        # Sauvegarde à la perte de focus
        def on_focus_out(event):
            new_value = line_edit.text().strip()
            self._save_constante(key, new_value)
            QLineEdit.focusOutEvent(line_edit, event)
            
        line_edit.focusOutEvent = on_focus_out
        layout.addWidget(line_edit)
        
        return layout
        
    def _create_number_field(self, key: str, label: str, min_val: int = 0, max_val: int = 999) -> QHBoxLayout:
        """
        Crée un champ numérique avec sauvegarde automatique.
        
        Args:
            key: Clé de la constante
            label: Label à afficher
            min_val: Valeur minimale
            max_val: Valeur maximale
            
        Returns:
            Layout contenant le label et le champ
        """
        layout = QHBoxLayout()
        layout.addWidget(QLabel(f"{label} :"))
        
        spin_box = QSpinBox()
        spin_box.setMinimum(min_val)
        spin_box.setMaximum(max_val)
        
        value = constantes_manager.get_constante(key)
        if value is not None:
            try:
                spin_box.setValue(int(value))
            except (ValueError, TypeError):
                spin_box.setValue(min_val)
        
        # Sauvegarde à chaque changement
        spin_box.valueChanged.connect(
            lambda val: self._save_constante(key, val)
        )
        
        layout.addWidget(spin_box)
        layout.addStretch()
        
        return layout
        
    def _create_directory_field(self, key: str, label: str) -> QHBoxLayout:
        """
        Crée un champ pour sélectionner un dossier.
        
        Args:
            key: Clé de la constante
            label: Label à afficher
            
        Returns:
            Layout contenant le label, le champ et le bouton
        """
        layout = QHBoxLayout()
        layout.addWidget(QLabel(f"{label} :"))
        
        line_edit = QLineEdit()
        value = constantes_manager.get_constante(key)
        line_edit.setText(str(value) if value is not None else "")
        line_edit.setReadOnly(True)
        
        btn_browse = QPushButton("Parcourir...")
        btn_browse.clicked.connect(
            lambda: self._choose_directory(key, line_edit)
        )
        
        layout.addWidget(line_edit, stretch=1)
        layout.addWidget(btn_browse)
        
        return layout
        
    def _create_list_widget(self, key: str, label: str) -> QWidget:
        """
        Crée un widget de liste avec possibilité d'ajout uniquement.
        
        Args:
            key: Clé de la constante (liste)
            label: Label à afficher
            
        Returns:
            Widget contenant la liste et le champ d'ajout
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Label
        lbl = QLabel(f"<b>{label}</b>")
        layout.addWidget(lbl)
        
        # Liste
        list_widget = QListWidget()
        list_widget.setMaximumHeight(150)
        
        # Charger les valeurs existantes
        values = constantes_manager.get_constante(key) or []
        for value in values:
            list_widget.addItem(QListWidgetItem(str(value)))
        
        layout.addWidget(list_widget)
        
        # Zone d'ajout
        add_layout = QHBoxLayout()
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Nouvelle valeur...")
        
        btn_add = QPushButton("Ajouter")
        btn_add.clicked.connect(
            lambda: self._add_to_list(key, line_edit, list_widget)
        )
        
        # Permettre l'ajout avec la touche Entrée
        line_edit.returnPressed.connect(btn_add.click)
        
        add_layout.addWidget(line_edit)
        add_layout.addWidget(btn_add)
        layout.addLayout(add_layout)
        
        return container
        
    def _save_constante(self, key: str, value):
        """
        Sauvegarde une constante via le constantes_manager.
        
        Args:
            key: Clé de la constante
            value: Nouvelle valeur
        """
        try:
            constantes_manager.set_constante(key, value)
            self.constante_modified.emit(key, value)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de {key}: {e}")
            
    def _choose_directory(self, key: str, line_edit: QLineEdit):
        """
        Ouvre un dialogue de sélection de dossier.
        
        Args:
            key: Clé de la constante
            line_edit: Champ à mettre à jour
        """
        directory = QFileDialog.getExistingDirectory(
            self,
            "Choisir le dossier",
            line_edit.text()
        )
        
        if directory:
            line_edit.setText(directory)
            self._save_constante(key, directory)
            
    def _add_to_list(self, key: str, line_edit: QLineEdit, list_widget: QListWidget):
        """
        Ajoute un élément à une liste et sauvegarde.
        
        Args:
            key: Clé de la liste
            line_edit: Champ contenant la nouvelle valeur
            list_widget: Widget de liste à mettre à jour
        """
        value = line_edit.text().strip()
        if not value:
            return
            
        # Charger la liste actuelle
        current_list = constantes_manager.get_constante(key) or []
        
        # Éviter les doublons
        if value in current_list:
            line_edit.clear()
            return
            
        # Ajouter la nouvelle valeur
        current_list.append(value)
        
        # Sauvegarder
        try:
            constantes_manager.set_constante(key, current_list)
            
            # Mettre à jour l'affichage
            list_widget.addItem(QListWidgetItem(value))
            line_edit.clear()
            
            # Émettre le signal
            self.list_item_added.emit(key, value)
        except Exception as e:
            print(f"Erreur lors de l'ajout à {key}: {e}")
            
    def refresh(self):
        """Rafraîchit l'affichage (recharge depuis constantes_manager)."""
        # Recréer l'interface
        # Supprimer l'ancien layout
        old_layout = self.layout()
        if old_layout:
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                    
        self._init_ui()
