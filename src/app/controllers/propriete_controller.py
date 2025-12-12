# -*- coding: utf-8 -*-
"""
Contrôleur pour la gestion des propriétés du cabinet.
Gère la communication entre la vue et le modèle via les signaux Qt.
"""

from app.views.propriete_view import ProprieteView


class ProprieteController:
	"""Contrôleur pour la gestion des propriétés du cabinet/praticien."""
	
	def __init__(self):
		"""Initialise le contrôleur et connecte les signaux de la vue."""
		self.view = ProprieteView()
		self._connect_signals()
		
	def _connect_signals(self):
		"""Connecte les signaux de la vue aux slots du contrôleur."""
		self.view.constante_modified.connect(self._on_constante_modified)
		self.view.list_item_added.connect(self._on_list_item_added)
		
	def _on_constante_modified(self, key: str, value):
		"""
		Callback appelé quand une constante est modifiée.
		La sauvegarde est déjà effectuée par la vue via constantes_manager.
		
		Args:
			key: Clé de la constante modifiée
			value: Nouvelle valeur
		"""
		print(f"Constante modifiée: {key} = {value}")
		
	def _on_list_item_added(self, key: str, value: str):
		"""
		Callback appelé quand un élément est ajouté à une liste.
		La sauvegarde est déjà effectuée par la vue via constantes_manager.
		
		Args:
			key: Clé de la liste
			value: Valeur ajoutée
		"""
		print(f"Valeur ajoutée à {key}: {value}")
