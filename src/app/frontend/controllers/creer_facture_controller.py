import json
from os import path,environ,makedirs
from app.backend.model.facture import Facture
from app.backend.model.patient import Patient

import app.backend.services.constantes_manager as constantes_manager

from app.backend.model.ligneFacture import LigneFacture
from datetime import timedelta, datetime
import app.backend.services.constantes_manager as cm
import app.backend.services.facture_generator as fg
from app.backend.services.internet_API_thread_worker import APIRequestQueue
import webbrowser

from app.backend.services.patient_service import PatientService
from app.backend.services.rendezVous_service import RendezVousService
from app.backend.services.facture_service import FactureService
from app.backend.services.ligneFacture_service import LigneFactureService
from app.backend.services.typeRDV_service import TypeRDVService

from app.frontend.views.creer_facture_view import creerFactureView
from app.exceptions import CabiLibException, EntiteIntrouvableException, RegleMetierException
from app.frontend.widgetPersonalise.error_boxes import ExceptionHandler


class CreerFactureController:
    def __init__(self, model, view: creerFactureView):
    
        self.view: creerFactureView = view
        # Connecter les signaux de la vue aux méthodes du contrôleur
        self.view.facture_generer.connect(self.on_facture_generer)
        self.view.facture_preview.connect(self.on_facture_preview)
        self.view.date_changed.connect(self.on_date_changed)
        self.view.refresh.connect(self.on_refresh)
        self.view.set_patient_list(PatientService.get_all_patients())

    def on_refresh(self):
        self.view.set_patient_list(PatientService.get_all_patients())

    def facturer_patient(self, patient: Patient, start_date: datetime, end_date: datetime,preview=False) -> tuple[int,str]:
        """Facturer un patient pour les rendez-vous entre start_date et end_date.

        args:
            patient (Patient): Le patient à facturer.
            start_date (datetime): La date de début de la période de facturation.
            end_date (datetime): La date de fin de la période de facturation.

        returns:
            tuple[int,str]: L'ID de la facture créée et le chemin du PDF généré. Si aucun rendez-vous n'est facturé, retourne -1 et une chaîne vide.
        """
        liste_rdvs = RendezVousService.get_rendezvous_by_patient_and_date_range(patient.id, start_date, end_date)

        # Initialiser les listes pour catégoriser les rendez-vous
        rdvs_factures = []
        rdvs_patient_absent = []
        rdvs_a_renseigner = []
        annulation_factures = []
        lignes_facture = []

        #Calculer le bon numéro de facture
        facture = Facture(id=FactureService.generate_numero_facture(end_date), patient_id=patient.id, date_emission=datetime.today().date(), statut="IMPAYE",start_date=start_date,end_date=end_date)
        msg = f"""Facturation du patient {patient.prenom} {patient.nom} entre le {start_date} et le {end_date}\n
        numéro de facture : {facture.id}\n
        Liste des rendez-vous à facturer :
        {"\n".join([f"- RDV ID {rdv.id} le {rdv.date} avec statut de présence : {rdv.presence}" for rdv in liste_rdvs])}"""
        
        for rdv in liste_rdvs:
            # si le rendez-vous est déjà facturé on ne le compte pas dans les rendez-vous à facturer
            # on demande si on veut quand meme editer la facture sans ces rdvs
            
            if(rdv.facture_id is not None and rdv.facture_id!="-1"):
    
                if (rdv.facture_id not in annulation_factures):
                    annulation_factures.append(rdv.facture_id)
                    #on passe au rendez-vous d'après
                    continue
            
            if (rdv.presence == "Absent"):
                #si le patient est absent on ajoute le rdv à la liste des rdv ou il etait absent
                rdvs_patient_absent.append(rdv)
            elif (rdv.presence == "Présent"):
                
                # ca marche car les ids des types de rdv commencent à 1 et sont continus
                new_ligne = LigneFacture(idFacture=facture.id, idRendezVous=rdv.id, montant_facture=TypeRDVService.get_type_by_id(rdv.type_id).prix)
                rdv.facture_id = facture.id
                if(preview==False):
                    try :
                        FactureService.add_facture(facture)
                    except CabiLibException as e:
                        print(e)
                        pass
                    LigneFactureService.add_ligne(new_ligne)
                    RendezVousService.update_rendezvous(rdv.id, rdv)
                else :
                    lignes_facture.append(new_ligne)

                #a enlever peut-etre
                rdvs_factures.append(rdv)
            elif (rdv.presence == "A définir"):
                rdvs_a_renseigner.append(rdv)

            elif (rdv.presence == "Absent excusé" or rdv.presence == "Annulé"):
                
                rdv.facture_id = facture.id  # on marque que ce rdv ne sera pas facturé
                if(preview==False):
                    try : 
                        FactureService.add_facture(facture)
                    except CabiLibException as e:
                        pass
                    RendezVousService.update_rendezvous(rdv.id, rdv)
            else :
                pass
            

        # si un des rendez-vous n'a pas de statut de présence défini, on n'émet pas la facture
        if (len(rdvs_a_renseigner) > 0):
            msg = f"Le patient {patient.prenom} {patient.nom} a des rendez-vous sans statut de présence défini :\n"
            for rdv in rdvs_a_renseigner:
                msg += f"- Rendez-vous du {rdv.date.strftime('%d/%m/%Y à %H:%M')}\n"
            msg += "Veuillez renseigner le statut de présence avant de facturer."
            raise RegleMetierException(msg)
        
        if (len(annulation_factures) > 0):
            for fac in annulation_factures :
                # on ajoute les lignes de facture déjà existantes à la nouvelle facture
                lignes = LigneFactureService.get_lignes_by_facture_id(fac)
                for l in lignes :                    
                    rdv = RendezVousService.get_rendezvous_by_id(l.idRendezVous)
                    rdv.facture_id = facture.id
                    if(preview==False):
                        # si ce n'est pas une prévisualisation, on met à jour la base de données
                        try : 
                            FactureService.add_facture(facture)
                        except CabiLibException as e:
                            pass
                        
                        RendezVousService.update_rendezvous(rdv.id, rdv)
                    # on ajoute le rdv à la liste des rdvs facturés
                    rdvs_factures.append(rdv)

                    lfac_test = LigneFactureService.get_ligne(facture.id,rdv.id)
                    #Si ce n'est pas une prévisualisation, on ajoute la ligne de facture à la base de données
                    if (preview==False) :
                        # on évite les doublons
                        if(lfac_test is None) :
                            lfac = LigneFacture(idFacture=facture.id, idRendezVous=rdv.id, montant_facture=l.montant_facture)
                            try :
                                FactureService.add_facture(facture)
                            except CabiLibException as e:
                                pass
                            LigneFactureService.add_ligne(lfac)          

        # si le patient a des absences, on demande confirmation avant de facturer
        elif (len(rdvs_patient_absent) > 0):
            #date a partir de la quelle on voit si le patient à déjà été absent
            historique_date = start_date - cm.get_constante("HISTORIQUE_ABSENCE_JOURS")*timedelta(days=1)
            absence_precedentes = [rdv if(rdv.presence=="Absent") else None for rdv in RendezVousService.get_rendezvous_by_patient_and_date_range(patient.id, historique_date, start_date)]
            facture_ensemble = self.view.erreur_patient_absent(patient, rdvs_patient_absent,absence_precedentes)

            # peut importe le choix si on est pas en preview on crée la facture afin de sauvegarder le choix du practitien
            if preview== False :
                try :
                    FactureService.add_facture(facture)
                except CabiLibException as e:
                    pass
            # si la facture existe ça lève une exception et on pass

            # si on confirme la facturation malgré les absences, on ne facture que 33€ par rendez-vous
            if(facture_ensemble) :

                for rdv in rdvs_patient_absent :
                    
                    rdv.facture_id = facture.id
                    if(preview==False):
                        RendezVousService.update_rendezvous(rdv.id, rdv)

                    rdvs_factures.append(rdv)
                    lfac = LigneFacture(idFacture=facture.id, idRendezVous=rdv.id, montant_facture=33)
                    if (preview==False):
                        LigneFactureService.add_ligne(lfac)
                    else :
                        lignes_facture.append(lfac)
            else :
                # on marque le chois du praticien en mettant le montant des rendez-vous absents à 0
                for rdv in rdvs_patient_absent:
                    
                    rdv.facture_id = facture.id
                    if (preview==False):
                        RendezVousService.update_rendezvous(rdv.id, rdv)

                    rdvs_factures.append(rdv)
                    lfac = LigneFacture(idFacture=facture.id, idRendezVous=rdv.id, montant_facture=0)
                    if (preview==False):
                        LigneFactureService.add_ligne(lfac)
                    else:
                        lignes_facture.append(lfac)

        # créer la facture si on a des rendez-vous à facturer
        if (len(rdvs_factures) > 0):
            filename = f"{facture.id+" "+(patient.acronyme if patient.acronyme is not None else '')}.pdf"
            if (preview==False):
                try :
                    FactureService.add_facture(facture)
                except CabiLibException as e:
                    self.view.afficher_message(str(e))
                
                lfacs = LigneFactureService.get_lignes_by_facture_id(facture.id)
                
                
                basepath = constantes_manager.get_constante("FACTURES_DIR")
                fac_path = facture.start_date.strftime("%Y-%m")
                abs_dir = path.abspath(path.join(basepath, fac_path))
                if not path.exists(abs_dir):
                    makedirs(abs_dir)
                abs_file = path.join(abs_dir, filename)

                fp = fg.create_and_save(facture, patient, lfacs, annulation_factures,start_date,end_date,abs_file)

            else :
                basepath = path.join(environ.get("APPDATA"),"CabiLib", 'facturesPreview').replace('\\', '/')
                fac_path = facture.date_emission.strftime("%Y-%m")
                abs_dir = path.abspath(path.join(basepath, fac_path))
                if not path.exists(abs_dir):
                    makedirs(abs_dir)
                abs_file = path.join(abs_dir, filename)

                fp = fg.create_and_save(facture, patient, lignes_facture, annulation_factures,start_date,end_date,abs_file, open_files=True)
            return facture.id,fp
        else :
            raise RegleMetierException(f"Aucune facture n'a pu être générée pour {patient.prenom} {patient.nom}\n(Aucun rendez-vous à facturer)")

    def on_facture_generer(self, start_date: datetime, end_date: datetime, patients: list)-> None:
        """Générer des factures de masse pour tous les patients entre start_date et end_date.
        args:
            start_date (datetime): La date de début de la période de facturation.
            end_date (datetime): La date de fin de la période de facturation.
        """
        factures_creees = []
        for pID in patients:
            try:
                patient = PatientService.get_patient_by_id(pID)
                facture_id,fp = self.facturer_patient(patient, start_date, end_date,False)
                factures_creees.append(FactureService.get_facture_by_id(facture_id))
                self.save_template_mail(patient, start_date, end_date, fp)
            except EntiteIntrouvableException:
                ExceptionHandler.handle(self.view, EntiteIntrouvableException(f"Patient ID {pID} non trouvé."))
                continue
            except CabiLibException as e:
                ExceptionHandler.handle(self.view, e)
                continue
                
        self.view.confirmation_facture_generee(factures_creees)

    def on_facture_preview(self, start_date: datetime, end_date: datetime, patients: list) -> None:
        """Prévisualiser des factures de masse pour tous les patients entre start_date et end_date.
        args:
            start_date (datetime): La date de début de la période de facturation.
            end_date (datetime): La date de fin de la période de facturation.
            patients (list): La liste des IDs des patients à facturer.
        """
        factures_creees = []
        for pID in patients:
            try :
                patient = PatientService.get_patient_by_id(pID)
                facture_id,fp = self.facturer_patient(patient, start_date, end_date,preview=True)
                factures_creees.append(Facture(id=facture_id,patient_id=patient.id))
                webbrowser.open_new_tab(fp)
            except EntiteIntrouvableException:
                ExceptionHandler.handle(self.view, EntiteIntrouvableException(f"Patient ID {pID} non trouvé."))
                continue
            except CabiLibException as e:
                ExceptionHandler.handle(self.view, e)
                continue
                
        self.view.confirmation_facture_generee(factures_creees)
    
    def on_date_changed(self, start_date: datetime, end_date: datetime) -> None:
        """Gérer le changement de date dans la vue de création de facture.
        args:
            start_date (datetime): La nouvelle date de début.
            end_date (datetime): La nouvelle date de fin.
        """
        end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, 999999)
        rdvs = RendezVousService.get_rendezvous_by_plage(start_date, end_date)
        patients = []
        seen_patient_ids = set()
        for rdv in rdvs:
            if rdv.patient_id in seen_patient_ids:
                continue
            try:
                patient = PatientService.get_patient_by_id(rdv.patient_id)
                patients.append(patient)
                seen_patient_ids.add(rdv.patient_id)
            except EntiteIntrouvableException:
                ExceptionHandler.handle(self.view, EntiteIntrouvableException(f"Patient ID {rdv.patient_id} non trouvé."))
                continue
        self.view.set_patient_list(patients)

    def save_template_mail(self, patient: Patient, start_date: datetime, end_date: datetime, facture_path: str) -> None:
        """Enregistrer un modèle d'email pour les factures.
        args:
            patient (Patient): Le patient pour lequel le modèle est enregistré.
            subject (str): Le sujet de l'email.
            body (str): Le corps de l'email.
        """
        attachements = [facture_path]
        attachements.append(path.join(environ['APPDATA'], 'CabiLib', 'RIB_Praticien.pdf').replace('\\','/'))
        attachements.append(path.join(environ['APPDATA'], 'CabiLib', 'logo.png').replace('\\','/'))
        APIRequestQueue.enqueue_api_request('gmail_save_draft', json.dumps({
            'to': patient.email,
            'subject': f'[Ergothérapie] Facture {patient.prenom} - du {start_date.date().strftime("%d-%m-%Y")} au {end_date.date().strftime("%d-%m-%Y")}',
            'body': f"""Bonjour,<br><br>
Veuillez trouver ci-joint votre <strong>facture pour la période du {start_date.date().strftime("%d-%m-%Y")} au {end_date.date().strftime("%d-%m-%Y")}</strong> concernant les séances d\'ergothérapie.<br>
Pour le règlement, plusieurs moyens de paiement sont possibles : <br><br>
1️⃣ <strong>Virement bancaire (préféré)</strong><br>
Merci d\'utiliser comme libellé : <br>
<strong>Nom + Prénom de l\'enfant + Mois de la facture</strong> <br>
(Exemple : Dupont Léa - Novembre)<br>
→ Les coordonnées bancaires sont jointes à ce mail.<br><br>
2️⃣ <strong>Chèque</strong><br>
A l\'ordre de : <strong>{cm.get_constante("PRACTITIONER_NAME")}</strong><br>
Merci de déposer le chèque <strong>dans la boite au lettre du cabinet</strong>, dans une enveloppe <strong>portant mon nom.</strong><br><br>
3️⃣ <strong>Espèces</strong><br>
Vous pouvez également régler en espèces, à déposer <strong>dans la boite au lettre du cabinet</strong>, dans une enveloppe <strong>portant mon nom.</strong><br><br>
N'hésitez pas à me contacter si vous avez la moindre question.<br><br>
⚠️ <strong>Quel que soit le mode de paiement choisi, merci de m'informer de la date et du mode de règlement</strong>, afin de faciliter le suivi de votre dossier.⚠️<br>
Cordialement,<br><br>

{cm.get_constante("PRACTITIONER_NAME")} - Ergotherapeute D.E.<br>
{cm.get_constante("CABINET_ADDRESS")}<br>
{cm.get_constante("PRACTITIONER_PHONE")}<br>
<img src="cid:logo.png" alt="CabiLib Logo" width="100"/></body>""",
            'attachments': attachements
        }))