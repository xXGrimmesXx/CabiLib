# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (QWidget, QFormLayout, QLineEdit, QPushButton, QFileDialog, QHBoxLayout, QComboBox, QMessageBox)
from PySide6.QtCore import Signal

class ProprieteView(QWidget):
    
	enregistrer_clicked: Signal = Signal()
	refresh: Signal = Signal()
	
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Propriétés du cabinet")
		layout = QFormLayout()
		
		self.heure_debut_edit: QLineEdit= QLineEdit()
		self.heure_fin_edit: QLineEdit= QLineEdit()
		self.nom_edit: QLineEdit= QLineEdit()
		self.tel_edit: QLineEdit= QLineEdit()
		self.adresse_edit: QLineEdit= QLineEdit()
		self.factures_dir_edit: QLineEdit= QLineEdit()

		# Listes modifiables avec ComboBox + boutons
		self.amenagements_combo: QComboBox = QComboBox(); self.amenagements_combo.setEditable(True)
		self.amenagements_add_btn: QPushButton = QPushButton("Ajouter")
		self.amenagements_del_btn: QPushButton = QPushButton("Supprimer")
		self.amenagements_add_btn.clicked.connect(lambda: self.add_combo_value(self.amenagements_combo))
		self.amenagements_del_btn.clicked.connect(lambda: self.del_combo_value(self.amenagements_combo))
		amenagements_layout = QHBoxLayout(); amenagements_layout.addWidget(self.amenagements_combo); amenagements_layout.addWidget(self.amenagements_add_btn); amenagements_layout.addWidget(self.amenagements_del_btn)

		self.etat_suivi_combo: QComboBox = QComboBox(); self.etat_suivi_combo.setEditable(True)
		self.etat_suivi_add_btn: QPushButton = QPushButton("Ajouter")
		self.etat_suivi_del_btn: QPushButton = QPushButton("Supprimer")
		self.etat_suivi_add_btn.clicked.connect(lambda: self.add_combo_value(self.etat_suivi_combo))
		self.etat_suivi_del_btn.clicked.connect(lambda: self.del_combo_value(self.etat_suivi_combo))
		etat_suivi_layout = QHBoxLayout(); etat_suivi_layout.addWidget(self.etat_suivi_combo); etat_suivi_layout.addWidget(self.etat_suivi_add_btn); etat_suivi_layout.addWidget(self.etat_suivi_del_btn)

		self.niveau_scolaire_combo: QComboBox = QComboBox(); self.niveau_scolaire_combo.setEditable(True)
		self.niveau_scolaire_add_btn: QPushButton = QPushButton("Ajouter")
		self.niveau_scolaire_del_btn: QPushButton = QPushButton("Supprimer")
		self.niveau_scolaire_add_btn.clicked.connect(lambda: self.add_combo_value(self.niveau_scolaire_combo))
		self.niveau_scolaire_del_btn.clicked.connect(lambda: self.del_combo_value(self.niveau_scolaire_combo))
		niveau_scolaire_layout = QHBoxLayout(); niveau_scolaire_layout.addWidget(self.niveau_scolaire_combo); niveau_scolaire_layout.addWidget(self.niveau_scolaire_add_btn); niveau_scolaire_layout.addWidget(self.niveau_scolaire_del_btn)

		self.type_telephone_combo: QComboBox = QComboBox(); self.type_telephone_combo.setEditable(True)
		self.type_telephone_add_btn: QPushButton = QPushButton("Ajouter")
		self.type_telephone_del_btn: QPushButton = QPushButton("Supprimer")
		self.type_telephone_add_btn.clicked.connect(lambda: self.add_combo_value(self.type_telephone_combo))
		self.type_telephone_del_btn.clicked.connect(lambda: self.del_combo_value(self.type_telephone_combo))
		type_telephone_layout = QHBoxLayout(); type_telephone_layout.addWidget(self.type_telephone_combo); type_telephone_layout.addWidget(self.type_telephone_add_btn); type_telephone_layout.addWidget(self.type_telephone_del_btn)

		self.durees_rdv_combo: QComboBox = QComboBox(); self.durees_rdv_combo.setEditable(True)
		self.durees_rdv_add_btn: QPushButton = QPushButton("Ajouter")
		self.durees_rdv_del_btn: QPushButton = QPushButton("Supprimer")
		self.durees_rdv_add_btn.clicked.connect(lambda: self.add_combo_value(self.durees_rdv_combo))
		self.durees_rdv_del_btn.clicked.connect(lambda: self.del_combo_value(self.durees_rdv_combo))
		durees_rdv_layout = QHBoxLayout(); durees_rdv_layout.addWidget(self.durees_rdv_combo); durees_rdv_layout.addWidget(self.durees_rdv_add_btn); durees_rdv_layout.addWidget(self.durees_rdv_del_btn)

		self.precision_planning_combo: QComboBox = QComboBox(); self.precision_planning_combo.setEditable(True)
		self.precision_planning_add_btn: QPushButton = QPushButton("Ajouter")
		self.precision_planning_del_btn: QPushButton = QPushButton("Supprimer")
		self.precision_planning_add_btn.clicked.connect(lambda: self.add_combo_value(self.precision_planning_combo))
		self.precision_planning_del_btn.clicked.connect(lambda: self.del_combo_value(self.precision_planning_combo))
		precision_planning_layout = QHBoxLayout(); precision_planning_layout.addWidget(self.precision_planning_combo); precision_planning_layout.addWidget(self.precision_planning_add_btn); precision_planning_layout.addWidget(self.precision_planning_del_btn)

		self.browse_btn: QPushButton = QPushButton("Parcourir…")
		self.browse_btn.clicked.connect(self.browse_dir)
		dir_layout = QHBoxLayout()
		dir_layout.addWidget(self.factures_dir_edit)
		dir_layout.addWidget(self.browse_btn)

		layout.addRow("Nom du praticien", self.nom_edit)
		layout.addRow("Téléphone", self.tel_edit)
		layout.addRow("Adresse du cabinet", self.adresse_edit)
		layout.addRow("Dossier des factures", dir_layout)
		layout.addRow("Aménagements", amenagements_layout)
		layout.addRow("États de suivi", etat_suivi_layout)
		layout.addRow("Niveaux scolaires", niveau_scolaire_layout)
		layout.addRow("Types de téléphone", type_telephone_layout)
		layout.addRow("Durées RDV (HH:mm)", durees_rdv_layout)
		layout.addRow("Heure début (ex: 07:00)", self.heure_debut_edit)
		layout.addRow("Heure fin (ex: 22:00)", self.heure_fin_edit)
		layout.addRow("Précision planning", precision_planning_layout)

		self.save_btn: QPushButton = QPushButton("Enregistrer")
		self.save_btn.clicked.connect(self.enregistrer_clicked.emit)
		layout.addRow(self.save_btn)

		self.setLayout(layout)
	
	def on_refresh(self):
		"""
		Émettre le signal de rafraîchissement des données
		"""
		self.refresh.emit()

	def browse_dir(self):
		"""Ouvrir une boîte de dialogue pour choisir un dossier
		"""
		dir = QFileDialog.getExistingDirectory(self, "Choisir le dossier des factures")
		if dir:
			self.factures_dir_edit.setText(dir)

	def set_values(self, nom: str, tel: str, adresse: str, factures_dir: str, amenagements: str, etat_suivi: str, niveau_scolaire: str, type_telephone: str, durees_rdv: str, heure_debut: str, heure_fin: str, precision_planning: str):
		"""
		Remplir les champs avec les valeurs fournies

		Args:
			nom (str): Nom du praticien
			tel (str): Numéro de téléphone
			adresse (str): Adresse du cabinet
			factures_dir (str): Dossier des factures
			amenagements (str): Aménagements (séparés par des virgules)
			etat_suivi (str): État de suivi (séparés par des virgules)
			niveau_scolaire (str): Niveau scolaire (séparés par des virgules)
			type_telephone (str): Type de téléphone (séparés par des virgules)
			durees_rdv (str): Durée des RDV (séparés par des virgules)
			heure_debut (str): Heure de début
			heure_fin (str): Heure de fin
			precision_planning (str): Précision du planning (séparés par des virgules)

		"""
		self.nom_edit.setText(nom)
		self.tel_edit.setText(tel)
		self.adresse_edit.setText(adresse)
		self.factures_dir_edit.setText(factures_dir)
		self.amenagements_combo.clear(); [self.amenagements_combo.addItem(x.strip()) for x in amenagements.split(',') if x.strip()]
		self.etat_suivi_combo.clear(); [self.etat_suivi_combo.addItem(x.strip()) for x in etat_suivi.split(',') if x.strip()]
		self.niveau_scolaire_combo.clear(); [self.niveau_scolaire_combo.addItem(x.strip()) for x in niveau_scolaire.split(',') if x.strip()]
		self.type_telephone_combo.clear(); [self.type_telephone_combo.addItem(x.strip()) for x in type_telephone.split(',') if x.strip()]
		self.durees_rdv_combo.clear(); [self.durees_rdv_combo.addItem(x.strip()) for x in durees_rdv.split(',') if x.strip()]
		self.heure_debut_edit.setText(heure_debut)
		self.heure_fin_edit.setText(heure_fin)
		self.precision_planning_combo.clear(); [self.precision_planning_combo.addItem(x.strip()) for x in precision_planning.split(',') if x.strip()]

	def get_values(self) -> dict:
		"""Récupérer les valeurs des champs sous forme de dictionnaire
		"""
		return {
			'nom': self.nom_edit.text(),
			'tel': self.tel_edit.text(),
			'adresse': self.adresse_edit.text(),
			'factures_dir': self.factures_dir_edit.text(),
			'amenagements': ','.join([self.amenagements_combo.itemText(i) for i in range(self.amenagements_combo.count())]),
			'etat_suivi': ','.join([self.etat_suivi_combo.itemText(i) for i in range(self.etat_suivi_combo.count())]),
			'niveau_scolaire': ','.join([self.niveau_scolaire_combo.itemText(i) for i in range(self.niveau_scolaire_combo.count())]),
			'type_telephone': ','.join([self.type_telephone_combo.itemText(i) for i in range(self.type_telephone_combo.count())]),
			'durees_rdv': ','.join([self.durees_rdv_combo.itemText(i) for i in range(self.durees_rdv_combo.count())]),
			'heure_debut': self.heure_debut_edit.text(),
			'heure_fin': self.heure_fin_edit.text(),
			'precision_planning': ','.join([self.precision_planning_combo.itemText(i) for i in range(self.precision_planning_combo.count())])
		}

	def add_combo_value(self, combo: QComboBox)-> None:
		"""
		Ajouter une valeur au combo si elle n'existe pas déjà
		"""
		text:str = combo.currentText().strip()
		if text and combo.findText(text) == -1:
			combo.addItem(text)
			combo.setCurrentText("")
		else:
			QMessageBox.information(self, "Info", "Valeur déjà présente ou vide.")

	def del_combo_value(self, combo: QComboBox)-> None:
		"""
		Supprimer la valeur sélectionnée dans le combo
		"""
		idx = combo.currentIndex()
		if idx >= 0:
			combo.removeItem(idx)
