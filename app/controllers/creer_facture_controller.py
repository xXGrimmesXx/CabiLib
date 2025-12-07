from app.model.facture import Facture
from app.model.patient import Patient
from app.model.rendezVous import RendezVous
from app.model.typeRDV import TypeRDV
from app.model.ligneFacture import LigneFacture
from datetime import timedelta, datetime
import utils.constantes_manager as cm
import utils.facture_generator as fg
# import utils.mail_sender as ms


class CreerFactureController:
    def __init__(self, model, view):
        self.patientModel = Patient
        self.factureModel = Facture
        self.rdvModel = RendezVous
        self.typeRDVModel = TypeRDV
        self.ligneFactureModel = LigneFacture
        self.view = view
        self.type_rdv_liste = self.typeRDVModel.getAllTypesRDV()
        # Connecter les signaux de la vue aux méthodes du contrôleur
        self.view.mass_facture_generer.connect(self.on_mass_facture_generer)
        self.view.single_facture_generer.connect(self.on_single_facture_generer)
        self.view.set_patient_list(self.patientModel.getAllPatients())

    def facturer_patient(self, patient, start_date, end_date) :
        liste_rdvs = self.rdvModel.getRendezVousByPatientAndDateRange(patient.id, start_date, end_date)
        rdvs_factures = []
        rdvs_patient_absent = []
        rdvs_a_renseigner = []
        annulation_factures = []
        factures_generees = []
        #Calculer le bon numéro de facture
        facture = Facture(Facture.generate_numero_facture(datetime.today()),patient.id)
        msg = f"""Facturation du patient {patient.prenom} {patient.nom} entre le {start_date} et le {end_date}\n
        numéro de facture : {facture.id}\n
        Liste des rendez-vous à facturer :
        {"\n".join([f"- RDV ID {rdv.id} le {rdv.date} avec statut de présence : {rdv.presence}" for rdv in liste_rdvs])}"""
        print(msg)
        
        for rdv in liste_rdvs:
            # si le rendez-vous est déjà facturé on ne le compte pas dans les rendez-vous à facturer
            # on demande si on veut quand meme editer la facture sans ces rdvs
            if(rdv.facture_id is not None and rdv.facture_id!="-1"):
                print("Le rendez-vous ID :", rdv.id, "a déjà une facture ID :", rdv.facture_id)
                annulation_factures.append(rdv.facture_id)
                #on passe au rendez-vous d'après
                continue

            if (rdv.presence == "Patient absent"):
                print("Le patient était absent au rendez-vous ID :", rdv.id)
                #si le patient est absent on ajoute le rdv à la liste des rdv ou il etait absent
                rdvs_patient_absent.append(rdv)
            elif (rdv.presence == "Patient présent"):
                print("Le patient était présent au rendez-vous ID :", rdv.id)
                # ca marche car les ids des types de rdv commencent à 1 et sont continus
                new_ligne = LigneFacture(facture.id,rdv.id,self.type_rdv_liste[rdv.type_id-1].prix)
                LigneFacture.addLigneFacture(new_ligne)
                rdv.facture_id = facture.id
                self.rdvModel.updateRendezVous(rdv.id, rdv)
                #a enlever peut-etre
                rdvs_factures.append(rdv)
            elif (rdv.presence == "A confirmer" or rdv.presence == "A renseigner"):
                print("Le statut de présence n'est pas défini pour le rendez-vous ID :", rdv.id)
                rdvs_a_renseigner.append(rdv)
            elif (rdv.presence == "Patient absent excusé" or rdv.presence == "Annulé par moi"):
                print("Le rendez-vous ID :", rdv.id, "ne sera pas facturé (présence :", rdv.presence,")")
                rdv.facture_id = -1  # on marque que ce rdv ne sera pas facturé
                self.rdvModel.updateRendezVous(rdv.id, rdv)
            else :
                print("Statut de présence inconnu pour le rendez-vous ID :", rdv.id,"\t",rdv.presence)

        # si un des rendez-vous n'a pas de statut de présence défini, on n'émet pas la facture
        if (len(rdvs_a_renseigner) > 0):
            self.view.erreur_completion_rdv(patient, rdvs_a_renseigner)
            return -1,""
        
        print("\nNombre de rendez-vous avec absence :", len(rdvs_patient_absent),"\n")
        if (len(annulation_factures) > 0):
            for fac in annulation_factures :
                lignes = LigneFacture.getAllLignesByFactureId(fac)
                for l in lignes :
                    print(rdv)
                    rdv = self.rdvModel.getRendezVousById(l.rdv_id)
                    rdv.facture_id = facture.id
                    self.rdvModel.updateRendezVous(rdv.id, rdv)
                    rdvs_factures.append(rdv)

                    lfac = LigneFacture(facture.id,rdv.id,l.montant_facture)
                    LigneFacture.addLigneFacture(lfac)


        # si le patient a des absences, on demande confirmation avant de facturer
        
        elif (len(rdvs_patient_absent) > 0):
            #date a partir de la quelle on voit si le patient à déjà été absent
            historique_date = start_date - cm.get_constante("HISTORIQUE_ABSENCE_JOURS")*timedelta(days=1)
            absence_precedentes = [rdv if(rdv.presence=="Patient absent") else None for rdv in self.rdvModel.getRendezVousByPatientAndDateRange(patient.id, historique_date, start_date)]
            facture_ensemble = self.view.erreur_patient_absent(patient, rdvs_patient_absent,absence_precedentes)

            # si on confirme la facturation malgré les absences, on ne facture que 33€ par rendez-vous
            if(facture_ensemble) :
                for rdv in rdvs_patient_absent :
                    
                    rdv.facture_id = facture.id
                    self.rdvModel.updateRendezVous(rdv.id, rdv)

                    #TODO peut etre à enlever
                    rdvs_factures.append(rdv)
                    lfac = LigneFacture(facture.id,rdv.id,33)
                    LigneFacture.addLigneFacture(lfac)
            else :
                # on marque le chois du praticien en mettant le montant des rendez-vous absents à 0
                for rdv in rdvs_patient_absent:
                    
                    rdv.facture_id = facture.id
                    self.rdvModel.updateRendezVous(rdv.id, rdv)

                    #TODO peut etre à enlever
                    rdvs_factures.append(rdv)
                    lfac = LigneFacture(facture.id,rdv.id,0)
                    LigneFacture.addLigneFacture(lfac)

        # créer la facture si on a des rendez-vous à facturer
        if (len(rdvs_factures) > 0):
            print("Création de la facture pour le patient :",patient.prenom,patient.nom)
            Facture.addFacture(facture)
            lfacs = LigneFacture.getAllLignesByFactureId(facture.id)
            fp = fg.create_and_save(facture, patient, lfacs, annulation_factures,start_date,end_date)
            return facture.id,fp
        else :
            print("Aucun rendez-vous à facturer pour le patient :",patient.prenom,patient.nom)
            return -1,""
        


    def on_mass_facture_generer(self, start_date, end_date):
        print("Génération de factures de masse du", start_date, "au", end_date)
        patients = self.patientModel.getAllPatients()
        factures_creees = []
        for patient in patients:
            factures_creees.append((self.facturer_patient(patient, start_date, end_date)))
        self.view.confirmation_facture_generee([Facture(fac[0],patient.id) for fac,patient in zip(factures_creees,patients) if fac[0]!=-1])

    def on_single_facture_generer(self, start_date, end_date, patient_id):
        print("Génération d'une facture pour le patient ID", patient_id, "du", start_date, "au", end_date)
        patient = self.patientModel.getPatientById(patient_id)
        facture_id,fp = self.facturer_patient(patient, start_date, end_date)
        if(facture_id!=-1) :
            self.view.confirmation_facture_generee([Facture(facture_id,patient.id)])
        else :
            self.view.erreur_generation_facture()