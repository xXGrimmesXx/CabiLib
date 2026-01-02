import json
from os import path,environ
from app.model.facture import Facture
from app.model.patient import Patient
from app.model.rendezVous import RendezVous
from app.model.typeRDV import TypeRDV
from app.model.ligneFacture import LigneFacture
from datetime import timedelta, datetime
import app.services.constantes_manager as cm
import app.services.facture_generator as fg
from app.services.internet_API_thread_worker import APIRequestQueue
import webbrowser

from app.views.creer_facture_view import creerFactureView


class CreerFactureController:
    def __init__(self, model, view: creerFactureView):
        self.patientModel: Patient = Patient
        self.factureModel: Facture = Facture
        self.rdvModel: RendezVous =Patient
        self.factureModel: Facture = Facture
        self.rdvModel: RendezVous = RendezVous
        self.typeRDVModel: TypeRDV = TypeRDV
        self.ligneFactureModel: LigneFacture = LigneFacture
        self.view: creerFactureView = view
        # Connecter les signaux de la vue aux méthodes du contrôleur
        self.view.mass_facture_generer.connect(self.on_mass_facture_generer)
        self.view.single_facture_generer.connect(self.on_single_facture_generer)
        self.view.single_facture_preview.connect(self.on_single_facture_preview)
        self.view.mass_facture_preview.connect(self.on_mass_facture_preview)
        self.view.refresh.connect(self.on_refresh)
        self.view.set_patient_list(self.patientModel.getAllPatients())

    def on_refresh(self):
        self.view.set_patient_list(self.patientModel.getAllPatients())

    def facturer_patient(self, patient: Patient, start_date: datetime, end_date: datetime,preview=False) -> tuple[int,str]:
        """Facturer un patient pour les rendez-vous entre start_date et end_date.

        args:
            patient (Patient): Le patient à facturer.
            start_date (datetime): La date de début de la période de facturation.
            end_date (datetime): La date de fin de la période de facturation.

        returns:
            tuple[int,str]: L'ID de la facture créée et le chemin du PDF généré. Si aucun rendez-vous n'est facturé, retourne -1 et une chaîne vide.
        """
        print("\n\n\n-----------------------------DEBUT EMISSION FACTURE----------------------------\n\n\n")
        print("Facturation du patient :",patient.prenom,patient.nom)
        print("Entre le", start_date, "et le", end_date)
        liste_rdvs = self.rdvModel.getRendezVousByPatientAndDateRange(patient.id, start_date, end_date)
        rdvs_factures = []
        rdvs_patient_absent = []
        rdvs_a_renseigner = []
        annulation_factures = []
        lignes_facture = []
        #Calculer le bon numéro de facture
        facture = Facture(Facture.generate_numero_facture(end_date),patient.id)
        msg = f"""Facturation du patient {patient.prenom} {patient.nom} entre le {start_date} et le {end_date}\n
        numéro de facture : {facture.id}\n
        Liste des rendez-vous à facturer :
        {"\n".join([f"- RDV ID {rdv.id} le {rdv.date} avec statut de présence : {rdv.presence}" for rdv in liste_rdvs])}"""
        print(msg)
        
        for rdv in liste_rdvs:
            # si le rendez-vous est déjà facturé on ne le compte pas dans les rendez-vous à facturer
            # on demande si on veut quand meme editer la facture sans ces rdvs
            print("\nTraitement du rendez-vous ID : ", rdv.id, " le ", rdv.date," présence : ",rdv.presence)
            
            if(rdv.facture_id is not None and rdv.facture_id!="-1"):
                print("Le rendez-vous ID :", rdv.id, "a déjà une facture ID :", rdv.facture_id)
                if (rdv.facture_id not in annulation_factures):
                    annulation_factures.append(rdv.facture_id)
                    #on passe au rendez-vous d'après
                    continue
            
            if (rdv.presence == "Absent"):
                print("Le patient était absent au rendez-vous ID :", rdv.id)
                #si le patient est absent on ajoute le rdv à la liste des rdv ou il etait absent
                rdvs_patient_absent.append(rdv)
            elif (rdv.presence == "Présent"):
                print("Le patient était présent au rendez-vous ID :", rdv.id)
                # ca marche car les ids des types de rdv commencent à 1 et sont continus
                new_ligne = LigneFacture(facture.id,rdv.id,self.typeRDVModel.getTypeRDVById(rdv.type_id).prix)
                rdv.facture_id = facture.id
                if(preview==False):
                    LigneFacture.addLigneFacture(new_ligne)
                    self.rdvModel.updateRendezVous(rdv.id, rdv)
                else :
                    lignes_facture.append(new_ligne)

                #a enlever peut-etre
                rdvs_factures.append(rdv)
            elif (rdv.presence == "A définir"):
                print("Le statut de présence n'est pas défini pour le rendez-vous ID :", rdv.id)
                rdvs_a_renseigner.append(rdv)
            elif (rdv.presence == "Absent excusé" or rdv.presence == "Annulé"):
                print("Le rendez-vous ID :", rdv.id, "ne sera pas facturé (présence :", rdv.presence,")")
                rdv.facture_id = -1  # on marque que ce rdv ne sera pas facturé
                if(preview==False):
                    self.rdvModel.updateRendezVous(rdv.id, rdv)
            else :
                print("Statut de présence inconnu pour le rendez-vous ID :", rdv.id,"\t",rdv.presence)

        # si un des rendez-vous n'a pas de statut de présence défini, on n'émet pas la facture
        if (len(rdvs_a_renseigner) > 0):
            self.view.erreur_completion_rdv(patient, rdvs_a_renseigner)
            return -1,""
        
        if (len(annulation_factures) > 0):
            for fac in annulation_factures :
                if (preview==False) :
                    lignes = LigneFacture.getAllLignesByFactureId(fac)
                else :
                    lignes = lignes_facture
                for l in lignes :                    
                    rdv = self.rdvModel.getRendezVousById(l.rdv_id)
                    rdv.facture_id = facture.id
                    if(preview==False):
                        self.rdvModel.updateRendezVous(rdv.id, rdv)
                    rdvs_factures.append(rdv)

                    lfac_test = LigneFacture.getLigneFacture(facture.id,rdv.id)
                    #on vérifie que la ligne de facture n'existe pas déjà avant de la recréer
                    if (preview==False) :
                        if(lfac_test is None) :
                            lfac = LigneFacture(facture.id,rdv.id,l.montant_facture)
                            LigneFacture.addLigneFacture(lfac)              

        # si le patient a des absences, on demande confirmation avant de facturer
        elif (len(rdvs_patient_absent) > 0):
            #date a partir de la quelle on voit si le patient à déjà été absent
            historique_date = start_date - cm.get_constante("HISTORIQUE_ABSENCE_JOURS")*timedelta(days=1)
            absence_precedentes = [rdv if(rdv.presence=="Absent") else None for rdv in self.rdvModel.getRendezVousByPatientAndDateRange(patient.id, historique_date, start_date)]
            facture_ensemble = self.view.erreur_patient_absent(patient, rdvs_patient_absent,absence_precedentes)

            # si on confirme la facturation malgré les absences, on ne facture que 33€ par rendez-vous
            if(facture_ensemble) :
                for rdv in rdvs_patient_absent :
                    
                    rdv.facture_id = facture.id
                    if(preview==False):
                        self.rdvModel.updateRendezVous(rdv.id, rdv)

                    #TODO peut etre à enlever
                    rdvs_factures.append(rdv)
                    lfac = LigneFacture(facture.id,rdv.id,33)
                    if (preview==False):
                        LigneFacture.addLigneFacture(lfac)
                    else :
                        lignes_facture.append(lfac)
            else :
                # on marque le chois du praticien en mettant le montant des rendez-vous absents à 0
                for rdv in rdvs_patient_absent:
                    
                    rdv.facture_id = facture.id
                    if (preview==False):
                        self.rdvModel.updateRendezVous(rdv.id, rdv)

                    #TODO peut etre à enlever
                    rdvs_factures.append(rdv)
                    lfac = LigneFacture(facture.id,rdv.id,0)
                    if (preview==False):
                        LigneFacture.addLigneFacture(lfac)
                    else:
                        lignes_facture.append(lfac)

        # créer la facture si on a des rendez-vous à facturer
        if (len(rdvs_factures) > 0):
            print("Création de la facture pour le patient :",patient.prenom,patient.nom)
            print("\n\n\n-----------------------------FIN EMISSION FACTURE----------------------------\n\n\n")
            if (preview==False):
                Facture.addFacture(facture)
                lfacs = LigneFacture.getAllLignesByFactureId(facture.id)
                fp = fg.create_and_save_pdf(facture, patient, lfacs, annulation_factures,start_date,end_date)
            else :
                fp = fg.create_and_save_html(facture, patient, lignes_facture, annulation_factures,start_date,end_date)
            return facture.id,fp
        else :
            print("Aucun rendez-vous à facturer pour le patient :",patient.prenom,patient.nom)
            return -1,""
        


    def on_mass_facture_generer(self, start_date: datetime, end_date: datetime)-> None:
        """Générer des factures de masse pour tous les patients entre start_date et end_date.
        args:
            start_date (datetime): La date de début de la période de facturation.
            end_date (datetime): La date de fin de la période de facturation.
        """

        print("Génération de factures de masse du", start_date, "au", end_date)
        patients = self.patientModel.getAllPatients()
        factures_creees = []
        for patient in patients:
            facture_id,fp = self.facturer_patient(patient, start_date, end_date)
            if(facture_id!=-1) :
                factures_creees.append(Facture(facture_id,patient.id))
                self.save_template_mail(patient, start_date, end_date, fp)
            else :
                self.view.erreur_generation_facture()
                
        self.view.confirmation_facture_generee(factures_creees)

    def on_single_facture_generer(self, start_date: datetime, end_date: datetime, patient_id: int)-> None:
        """Générer une facture pour un patient spécifique entre start_date et end_date.
        args:
            start_date (datetime): La date de début de la période de facturation.
            end_date (datetime): La date de fin de la période de facturation.
            patient_id (int): L'ID du patient pour lequel la facture est générée.
        """
        
        print("Génération d'une facture pour le patient ID", patient_id, "du", start_date, "au", end_date)
        patient = self.patientModel.getPatientById(patient_id)
        facture_id,fp = self.facturer_patient(patient, start_date, end_date)
        if(facture_id!=-1) :
            self.view.confirmation_facture_generee([Facture(facture_id,patient.id)])
            self.save_template_mail(patient, start_date, end_date, fp)
        else :
            self.view.erreur_generation_facture()

    def on_single_facture_preview(self, start_date: datetime, end_date: datetime, patient_id: int) -> None:
        """Prévisualiser une facture pour un patient spécifique entre start_date et end_date.
        args:
            start_date (datetime): La date de début de la période de facturation.
            end_date (datetime): La date de fin de la période de facturation.
            patient_id (int): L'ID du patient pour lequel la facture est prévisualisée.
        """
        print("Prévisualisation d'une facture pour le patient ID", patient_id, "du", start_date, "au", end_date)
        patient = self.patientModel.getPatientById(patient_id)
        facture_id,fp =self.facturer_patient(patient, start_date, end_date,preview=True)

        if(facture_id!=-1) :
            self.view.confirmation_facture_generee([Facture(facture_id,patient.id)])
            self.save_template_mail(patient, start_date, end_date, fp)
            webbrowser.open_new_tab(fp)
        else :
            self.view.erreur_generation_facture()


    def on_mass_facture_preview(self, start_date: datetime, end_date: datetime) -> None:
        """Prévisualiser des factures de masse pour tous les patients entre start_date et end_date.
        args:
            start_date (datetime): La date de début de la période de facturation.
            end_date (datetime): La date de fin de la période de facturation.
        """
        print("Prévisualisation de factures de masse du", start_date, "au", end_date)
        patients = self.patientModel.getAllPatients()
        factures_creees = []
        for patient in patients:
            facture_id,fp = self.facturer_patient(patient, start_date, end_date,preview=True)
            if(facture_id!=-1) :
                factures_creees.append(Facture(facture_id,patient.id))
                webbrowser.open_new_tab(fp)
            else :
                self.view.erreur_generation_facture()
                
        self.view.confirmation_facture_generee(factures_creees)

    def save_template_mail(self, patient: Patient, start_date: datetime, end_date: datetime, facture_path: str) -> None:
        """Enregistrer un modèle d'email pour les factures.
        args:
            patient (Patient): Le patient pour lequel le modèle est enregistré.
            subject (str): Le sujet de l'email.
            body (str): Le corps de l'email.
        """
        attachements = [facture_path]
        attachements.append(path.join(environ['APPDATA'], 'CabiLib', 'RIB_Praticien.pdf').replace('\\','/'))
        print(attachements)
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
Cordialement,<br>""",
            'attachments': attachements
        }))