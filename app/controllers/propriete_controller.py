# -*- coding: utf-8 -*-

from app.views.propritete_view import ProprieteView
from utils import constantes_manager

# Nouvelle version : tous les champs éditables

class ProprieteController:
	def refresh(self):
		self.load_properties()
	def __init__(self):
		self.view = ProprieteView()
		self.load_properties()
		self.view.enregistrer_clicked.connect(self.save_properties)

	def load_properties(self):
		try:
			nom = constantes_manager.get_constante('PRACTITIONER_NAME')
			tel = constantes_manager.get_constante('PRACTITIONER_PHONE')
			adresse = constantes_manager.get_constante('CABINET_ADDRESS')
			factures_dir = constantes_manager.get_constante('FACTURES_DIR')
			amenagements = ','.join(constantes_manager.get_constante('AMENAGEMENTS_OPTIONS'))
			etat_suivi = ','.join(constantes_manager.get_constante('ETAT_SUIVI_OPTIONS'))
			niveau_scolaire = ','.join(constantes_manager.get_constante('NIVEAU_SCOLAIRE_OPTIONS'))
			type_telephone = ','.join(constantes_manager.get_constante('TYPE_TELEPHONE_OPTIONS'))
			durees_rdv = ','.join(constantes_manager.get_constante('DUREES_RDV'))
			heure_debut = constantes_manager.get_constante('HEURE_DEBUT')
			heure_fin = constantes_manager.get_constante('HEURE_FIN')
			precision_planning = ','.join([str(x) for x in constantes_manager.get_constante('PRECISION_PLANNING')])
		except Exception as e:
			print("Erreur lecture Constantes.json:", e)
			nom = tel = adresse = factures_dir = ''
			amenagements = etat_suivi = niveau_scolaire = type_telephone = durees_rdv = heure_debut = heure_fin = precision_planning = ''
		self.view.set_values(
			nom, tel, adresse, factures_dir,
			amenagements, etat_suivi, niveau_scolaire, type_telephone,
			durees_rdv, heure_debut, heure_fin, precision_planning
		)

	def save_properties(self):
		vals = self.view.get_values()
		try:
			constantes_manager.set_constante('PRACTITIONER_NAME', vals['nom'])
			constantes_manager.set_constante('PRACTITIONER_PHONE', vals['tel'])
			constantes_manager.set_constante('CABINET_ADDRESS', vals['adresse'])
			constantes_manager.set_constante('FACTURES_DIR', vals['factures_dir'])
			constantes_manager.set_constante('AMENAGEMENTS_OPTIONS', [x.strip() for x in vals['amenagements'].split(',') if x.strip()])
			constantes_manager.set_constante('ETAT_SUIVI_OPTIONS', [x.strip() for x in vals['etat_suivi'].split(',') if x.strip()])
			constantes_manager.set_constante('NIVEAU_SCOLAIRE_OPTIONS', [x.strip() for x in vals['niveau_scolaire'].split(',') if x.strip()])
			constantes_manager.set_constante('TYPE_TELEPHONE_OPTIONS', [x.strip() for x in vals['type_telephone'].split(',') if x.strip()])
			constantes_manager.set_constante('DUREES_RDV', [x.strip() for x in vals['durees_rdv'].split(',') if x.strip()])
			constantes_manager.set_constante('HEURE_DEBUT', vals['heure_debut'])
			constantes_manager.set_constante('HEURE_FIN', vals['heure_fin'])
			# precision_planning: convert to int if possible
			precision = [int(x.strip()) if x.strip().isdigit() else x.strip() for x in vals['precision_planning'].split(',') if x.strip()]
			constantes_manager.set_constante('PRECISION_PLANNING', precision)
		except Exception as e:
			print("Erreur écriture Constantes.json:", e)
		self.load_properties()
