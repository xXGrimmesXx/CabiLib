from datetime import timedelta, datetime
from weasyprint import HTML
from os import path, environ, makedirs
from sys import path as sys_path
from base64 import b64encode
import traceback
import app.backend.services.constantes_manager as cm
# Import des modèles existants
from app.backend.model.facture import Facture
from app.backend.model.patient import Patient
from app.backend.model.ligneFacture import LigneFacture
from app.backend.model.typeRDV import TypeRDV
from app.backend.model.rendezVous import RendezVous
sys_path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))) or '.')
from app.backend.services import constantes_manager

def format_date_fr(date_obj):
    """Transforme une date datetime en chaîne française (ex: 13 janvier 2024)"""
    if not date_obj: return ""
    mois = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
        7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
    }
    return f"{date_obj.day} {mois[date_obj.month]} {date_obj.year}"

def generate_redevance_html(date_debut: datetime, date_fin: datetime) -> bytes:
    """Génère le contenu HTML d'une redevance à partir des données fournies.
    Args:
        list_redevance (list): Liste contenant les informations de la redevance. sous la forme :
        [
        patient : [
            patient (Patient),
            typeRDV : [
                typeRDV (TypeRDV),
                rdv : [
                    rdv (RendezVous),
                    ligneFacture (LigneFacture)
                ]
            ]
            nb_seances : int,
            montant_total : float
        ]
        date_debut (datetime): Date de début de la période de facturation.
        date_fin (datetime): Date de fin de la période de facturation.
    Returns:
        str: Contenu HTML de la redevance.
    """
    # --- 1. Chargement des constantes ---
    PRACTITIONER_NAME = constantes_manager.get_constante("PRACTITIONER_NAME") 
    PRACTITIONER_PHONE = constantes_manager.get_constante("PRACTITIONER_PHONE") 
    CABINET_ADDRESS = constantes_manager.get_constante("CABINET_ADDRESS") 
    PRACTITIONER_SIRET = constantes_manager.get_constante("SIRET") 
    PRACTITIONER_APE = constantes_manager.get_constante("APE") 
    RESPONSABLE_CABINET_NAME = constantes_manager.get_constante("CABINET_RESPONSABLE_NAME")
    RESPONSABLE_PHONE = constantes_manager.get_constante("CABINET_RESPONSABLE_PHONE")
    RESPONSABLE_APE = constantes_manager.get_constante("CABINET_RESPONSABLE_APE")
    RESPONSABLE_SIRET = constantes_manager.get_constante("CABINET_RESPONSABLE_SIRET")
    NOM_CABINET = constantes_manager.get_constante("CABINET_NAME")
    REDEVANCE_FACTOR_RAW = constantes_manager.get_constante("REDEVANCE_FACTOR")

    # --- Validation des constantes ---
    constantes_requises = {
        "PRACTITIONER_NAME": PRACTITIONER_NAME,
        "PRACTITIONER_PHONE": PRACTITIONER_PHONE,
        "CABINET_ADDRESS": CABINET_ADDRESS,
        "SIRET": PRACTITIONER_SIRET,
        "APE": PRACTITIONER_APE,
        "CABINET_RESPONSABLE_NAME": RESPONSABLE_CABINET_NAME,
        "CABINET_RESPONSABLE_PHONE": RESPONSABLE_PHONE,
        "CABINET_RESPONSABLE_APE": RESPONSABLE_APE,
        "CABINET_RESPONSABLE_SIRET": RESPONSABLE_SIRET,
        "CABINET_NAME": NOM_CABINET,
        "REDEVANCE_FACTOR": REDEVANCE_FACTOR_RAW,
    }
    
    constantes_manquantes = [nom for nom, valeur in constantes_requises.items() if not valeur]
    if constantes_manquantes:
        raise ValueError(f"Constantes manquantes ou vides : {', '.join(constantes_manquantes)}")
    
    REDEVANCE_FACTOR = float(REDEVANCE_FACTOR_RAW) / 100

    # --- 2. Gestion du Logo ---
    logo_file = path.join(environ.get("APPDATA"),"CabiLib", 'logo.png').replace('\\', '/')
    logo_base64 = ''
    try:
        with open(logo_file, 'rb') as img_f:
            logo_bytes = img_f.read()
            logo_base64 = b64encode(logo_bytes).decode('utf-8')
    except Exception:
        traceback.print_exc()
        logo_base64 = ''
    
    logo_img_tag = f'<img src="data:image/png;base64,{logo_base64}" class="logo-img" alt="Logo" />' if logo_base64 else ''
    
    # --- 2b. Gestion de la Signature ---
    signature_file = path.join(environ.get("APPDATA"),"CabiLib", 'signature.png').replace('\\', '/')
    signature_base64 = ''
    try:
        with open(signature_file, 'rb') as img_f:
            signature_bytes = img_f.read()
            signature_base64 = b64encode(signature_bytes).decode('utf-8')
    except Exception:
        traceback.print_exc()
        signature_base64 = ''
    
    signature_img_tag = f'<img src="data:image/jpeg;base64,{signature_base64}" class="signature-img" alt="Signature" />' if signature_base64 else ''
    
    # --- 3. Préparation des données ---
    
    DATE_EMISSION_STR = format_date_fr(date_fin+timedelta(days=1))
    

    # Texte Période
    texte_periode = f"Période du {format_date_fr(date_debut)} au {format_date_fr(date_fin)}"

    # --- 4. Génération des lignes HTML du tableau ---
    

    patients = Patient.getAllPatients()
    types_rdv = TypeRDV.getAllTypesRDV()
    final_data = []

    for patient in patients:
        patient_dict = {"patient": patient, "type_rdv": [], "montant_total": 0.0, "nb_seances_total": 0}

        rdv_absent = TypeRDV(-1, "Facturation des séances non décommandées ","",33,0,"","",False)
        absent_dict = {"type_rdv": rdv_absent, "ligne_facture": [], "dates_seances": [], "montant_total": 0.0, "nb_seances": 0}

        for type_rdv in types_rdv:
            rdvs = RendezVous.get_by_patient_id_and_date_range_and_type_id(patient.id, date_debut, date_fin, type_rdv.id)
            rdv_dict = {"type_rdv": type_rdv, "dates_seances": [], "montant_total": 0.0, "nb_seances": 0}

            for rdv in rdvs:
                #Ligne facture la plus récente pour ce rendez-vous
                l_fac = LigneFacture.getLigneFacture(rdv.facture_id,rdv.id)
                # si une ligne de facture existe pour ce rendez-vous, on l'ajoute au dictionnaire du patient
                if (l_fac is not None):

                    if (rdv.presence == "Absent" and l_fac.montant_facture != 0):
                        absent_dict["montant_total"] += l_fac.montant_facture
                        absent_dict["dates_seances"].append(rdv.date)
                        absent_dict["nb_seances"] += 1
                    else : 
                        rdv_dict["dates_seances"].append(rdv.date)
                        rdv_dict["montant_total"] += l_fac.montant_facture
                        rdv_dict["nb_seances"] += 1

            # On ajoute le type de rdv seulement s'il y à des séances facturées pour ce type de rdv
            if rdv_dict["montant_total"] > 0:
                patient_dict["type_rdv"].append(rdv_dict)
                patient_dict["montant_total"] += rdv_dict["montant_total"]
                patient_dict["nb_seances_total"] += rdv_dict["nb_seances"]

        # On ajoute la section des absences seulement s'il y à des absences facturées
        if absent_dict["montant_total"] > 0:
            patient_dict["type_rdv"].append(absent_dict)
            patient_dict["montant_total"] += absent_dict["montant_total"]
            patient_dict["nb_seances_total"] += absent_dict["nb_seances"]

        final_data.append(patient_dict)


        final_data.sort(key=lambda x: x["patient"].nom if x["patient"].nom is not None else "")

    trs_html = """
    <table class='redevance'>
        <thead>
            <tr>
            <th>Patient</th>
            <th>Type RDV</th>
            <th>Date</th>
            <th>Prix</th>
            <th>Total type</th>
            <th>Total patient</th>
            </tr>
        </thead>
        <tbody>"""
    for patient_idx, patient_dict in enumerate(final_data):
        for typeRDVi in range(0,len(patient_dict["type_rdv"])) :
            for date_seance_i in range(0,len(patient_dict["type_rdv"][typeRDVi]["dates_seances"])) :
                # Déterminer si c'est la dernière ligne de données
                is_last_patient = (patient_idx == len(final_data) - 1)
                is_last_type = (typeRDVi == len(patient_dict["type_rdv"]) - 1)
                is_last_date = (date_seance_i == len(patient_dict["type_rdv"][typeRDVi]["dates_seances"]) - 1)
                last_row_class = ' last-data-row' if (is_last_patient and is_last_type and is_last_date) else ''

                # Nouveau patient + nouveau type de rdv
                if (typeRDVi == 0 and date_seance_i == 0) :
                    trs_html+=f"""
                    <tr class="patient-start{last_row_class}">
                        <td rowspan="{patient_dict["nb_seances_total"]}">{patient_dict["patient"].nom + " " + patient_dict["patient"].prenom}</td>
                        <td rowspan = "{patient_dict["type_rdv"][typeRDVi]["nb_seances"]}">{patient_dict["type_rdv"][typeRDVi]["type_rdv"].nom}</td>
                        <td>{patient_dict["type_rdv"][typeRDVi]["dates_seances"][date_seance_i].strftime("%d/%m/%Y")}</td>
                        <td rowspan ="{patient_dict["type_rdv"][typeRDVi]["nb_seances"]}">{patient_dict["type_rdv"][typeRDVi]["type_rdv"].prix} €</td>
                        <td rowspan="{patient_dict["type_rdv"][typeRDVi]["nb_seances"]}">{patient_dict["type_rdv"][typeRDVi]["montant_total"]} €</td>
                        <td rowspan="{patient_dict["nb_seances_total"]}">{patient_dict["montant_total"]} €</td>
                    </tr>"""

                # Nouveau type de rdv pour le même patient
                elif (date_seance_i == 0) :
                    trs_html+=f"""
                    <tr class="type-start{last_row_class}">
                        <td rowspan = "{patient_dict["type_rdv"][typeRDVi]["nb_seances"]}">{patient_dict["type_rdv"][typeRDVi]["type_rdv"].nom}</td>
                        <td>{patient_dict["type_rdv"][typeRDVi]["dates_seances"][date_seance_i].strftime("%d/%m/%Y")}</td>
                        <td rowspan ="{patient_dict["type_rdv"][typeRDVi]["nb_seances"]}">{patient_dict["type_rdv"][typeRDVi]["type_rdv"].prix} €</td>
                        <td rowspan="{patient_dict["type_rdv"][typeRDVi]["nb_seances"]}">{patient_dict["type_rdv"][typeRDVi]["montant_total"]} €</td>
                    </tr>"""

                # Même type de rdv pour le même patient
                else : 
                    trs_html+=f""" 
                    <tr class="{last_row_class.strip()}"> 
                        <td>{patient_dict["type_rdv"][typeRDVi]["dates_seances"][date_seance_i].strftime("%d/%m/%Y")}</td> 
                    </tr>"""
    total_general = sum(p["montant_total"] for p in final_data)
    trs_html += f"""
    <tr class="total-row total-row-first">
        <td colspan="3" class="td-no-border"></td>
        <td colspan="2" class="td-total-content td-total-first" style="text-align: right; font-weight: bold;">Total général :</td>
        <td class="td-total-content" style="font-weight: bold;">{total_general} €</td>
    </tr>

    <tr class="total-row">
        <td colspan="3" class="td-no-border"></td>
        <td colspan="2" class="td-total-content td-total-first" style="text-align: right; font-weight: bold;">Total redevance :</td>
        <td class="td-total-content" style="font-weight: bold;">{total_general*REDEVANCE_FACTOR} €</td>
    </tr>
    </tbody></table>"""
                    
            

    # --- 5. Template HTML ---
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 40px 50px 130px 50px; 
            }}
            
            body {{
                font-family: Arial, sans-serif;
                font-size: 10pt;
                color: #000;
                line-height: 1.3;
            }}

            /* --- LAYOUT HEADER (2 Colonnes via table) --- */
            .header-container {{
                display: table;
                width: 100%;
                margin-bottom: 20px;
                border-bottom: 2px solid #333;
                padding-bottom: 12px;
            }}
            .left-column {{
                display: table-cell;
                width: 50%;
                vertical-align: top;
                text-align: left;
                padding-right: 15px;
            }}
            .right-column {{
                display: table-cell;
                width: 50%;
                vertical-align: top;
                text-align: right;
                padding-left: 15px;
            }}

            .logo-img {{
                width: 80px;
                height: auto;
                margin-bottom: 6px;
            }}

            .practitioner-info {{
                font-size: 10pt;
                line-height: 1.5;
            }}

            a{{ color: inherit; text-decoration: none; }}

            .practitioner-name {{
                font-weight: bold;
                font-size: 11pt;
                margin-bottom: 4px;
            }}

            /* --- TABLEAU --- */
            table.redevance th{{
                border-left: 3px solid #000;
                border-right: 3px solid #000;
                border-top: 3px solid #000;
                border-bottom: 3px solid #000;
                padding: 6px 8px; 
                background-color: #AFCFBE;
                text-align: center;
                font-size: 10pt;
            }}
            table.redevance {{
                border-collapse: collapse;
                border: none;
                width: auto;
                font-family: Arial, sans-serif;
                font-size: 8pt;
                text-align: center;
                margin-top: 32px;
            }}

            table.redevance td {{
                border-left: 3px solid #000;
                border-right: 3px solid #000;
                border-top: 0px solid transparent;
                border-bottom: 0px solid transparent;
                padding: 4px 6px;
                vertical-align: middle;
                text-align: center;
                white-space: nowrap;
                width: 1%;
            }}
            /* Première colonne - bordure gauche */
            table.redevance td:first-child,
            table.redevance th:first-child {{
                border-left: 3px solid #000;
            }}
            /* Dernière colonne - bordure droite */
            table.redevance td:last-child,
            table.redevance th:last-child {{
                border-right: 3px solid #000;
            }}
            /* Ligne de séparation entre patients */
            tr.patient-start > * {{
                border-top: 3px solid #000 !important;
            }}
            /* Ligne de séparation entre types de rendez-vous */
            tr.type-start > * {{
                border-top: 2px dotted #000 !important;
            }}

            /* Dernière ligne de données - bordure du bas */
            tr.last-data-row > td {{
                border-bottom: 3px solid #000 !important;
            }}

            /* Ligne du total - cellules vides sans bordure */
            table.redevance tr.total-row td.td-no-border {{
                border: none !important;
            }}

            /* Première ligne du total - bordure top pour fermer le tableau */
            table.redevance tr.total-row-first td.td-no-border {{
                border-top: 3px solid #000 !important;
                border-left: none !important;
                border-right: none !important;
                border-bottom: none !important;
            }}

            /* Ligne du total - cellules avec contenu */
            table.redevance tr.total-row td.td-total-content {{
                border: 3px solid #000;
            }}
            table.redevance tr.total-row td.td-total-first {{
                border-left: 3px solid #000 !important;
            }}

            /* --- SIGNATURE --- */
            .signature-block {{
                margin-top: 40px;
                float: right;
                width: 40%;
                text-align: right;
            }}
            .signature-img {{
                max-width: 150px;
                height: auto;
                margin-top: 10px;
            }}
            .signature-line {{
                margin-top: 40px;
                border-top: 1px solid #000;
                width: 150px;
                margin-left: auto;
                text-align: center;
                padding-top: 5px;
                font-size: 9pt;
            }}
        </style>
    </head>
    <body>
        <div style="display: table; width: 100%; margin-bottom: 10px;">
            <div style="display: table-cell; vertical-align: middle; width: 100px;">{logo_img_tag}</div>
            <div style="display: table-cell; vertical-align: middle; text-align: center;">
                <h1 style="margin: 0; color : #AFCFBE;">Redevance Cabinet {NOM_CABINET}</h1>
                <p style="margin: 4px 0 0 0; font-size: 10pt; color : #AFCFBE;">{CABINET_ADDRESS}</p>
                <p></p>
                <p style="margin: 4px 0 0 0; font-size: 10pt; color : #AFCFBE;">{texte_periode}</p>
            </div>
            <div style="display: table-cell; width: 100px;"></div>
        </div>

        <div class="header-container">
            
            <div class="left-column">
                <div class="practitioner-info">
                    <div class="practitioner-name">{RESPONSABLE_CABINET_NAME}</div>
                    <div>Tel : {RESPONSABLE_PHONE}</div>
                    <div>APE : {RESPONSABLE_APE}</div>
                    <div>N° Siret : {RESPONSABLE_SIRET}</div>
                </div>
            </div>
            <div class="right-column"> 
                <div class="practitioner-info">
                    <div class="practitioner-name">{PRACTITIONER_NAME}</div>
                    <div>Tel : {PRACTITIONER_PHONE}</div>
                    <div>APE : {PRACTITIONER_APE}</div>
                    <div>N° Siret : {PRACTITIONER_SIRET}</div>
                </div>
            </div>

        </div>

        <p style="text-align: right; margin: 20px 0 10px 0;">A Plaisir, le {DATE_EMISSION_STR}</p>

        {trs_html}

        <div class="signature-block">
            <div style="margin-bottom: 5px;">{PRACTITIONER_NAME.upper()}</div>
            {signature_img_tag}
        </div>

    </body>
    </html>
    """

    return html_content

def generate_redevance_pdf(html_content: str) -> bytes:
    
    pdf = HTML(string=html_content).write_pdf()
    return pdf

def save_redevance_pdf(pdf_bytes: bytes, save_path:str ,filename: str) -> None:
    abs_dir = path.abspath(save_path)
    if not path.exists(abs_dir):
        makedirs(abs_dir)
    abs_file = path.join(abs_dir, filename)
    with open(abs_file, 'wb') as f:
        f.write(pdf_bytes)

def create_and_save_pdf (date_debut: datetime, date_fin: datetime) -> str:
    html_content = generate_redevance_html(date_debut, date_fin)
    pdf = generate_redevance_pdf(html_content)
    filename = f"redevance_{date_debut.strftime('%Y-%m')}_{cm.get_constante('PRACTITIONER_NAME')}.pdf"
    basepath = constantes_manager.get_constante("FACTURES_DIR")
    fac_path = date_fin.strftime("%Y")
    save_redevance_pdf(pdf, path.join(basepath, fac_path), filename)
    return path.join(basepath, fac_path, filename)

def create_and_save_html (date_debut: datetime, date_fin: datetime) -> str:
    html_content = generate_redevance_html(date_debut, date_fin)
    filename = f"redevance_{date_debut.strftime('%Y-%m')}_{cm.get_constante('PRACTITIONER_NAME')}.html"

    #dossier général des preview de redevance
    basepath = path.join(environ.get("APPDATA"),"CabiLib", 'RedevancePreview').replace('\\', '/')

    # dossier des previews de l'année
    fac_path = date_debut.strftime("%Y")

    #Chemin total
    abs_dir = path.abspath(path.join(basepath, fac_path))

    #Créer le dossier s'il n'existe pas
    if not path.exists(abs_dir):
        makedirs(abs_dir)
    abs_file = path.join(abs_dir, filename)
    with open(abs_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return abs_file
