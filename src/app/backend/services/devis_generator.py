from datetime import timedelta, datetime
from weasyprint import HTML
from os import path, environ, makedirs
from sys import path as sys_path
from base64 import b64encode
import traceback

# Import des modèles existants
from app.backend.model.patient import Patient
from app.backend.model.devis import Devis
from app.backend.model.acte_devis import ActeDevis

# Import des services existants
from app.backend.services.typeRDV_service import TypeRDVService
from app.exceptions import RegleMetierException

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

def generate_devis_html(devis : Devis, patient: Patient, actes: list[ActeDevis]) -> bytes:
    # --- 1. Chargement des constantes ---
    PRACTITIONER_NAME = constantes_manager.get_constante("PRACTITIONER_NAME") 
    PRACTITIONER_PHONE = constantes_manager.get_constante("PRACTITIONER_PHONE") 
    CABINET_ADDRESS = constantes_manager.get_constante("CABINET_ADDRESS") 
    PRACTITIONER_EMAIL = constantes_manager.get_constante("PRACTITIONER_EMAIL") 
    SIRET = constantes_manager.get_constante("SIRET") 
    APE = constantes_manager.get_constante("APE") 
    ADELI = constantes_manager.get_constante("ADELI")
    VALIDITE_DEVIS_DAYS = constantes_manager.get_constante("VALIDITE_DEVIS_DAYS")


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
    if devis.req_sign :
        signature_patient_bloc = """<div class="signature-patient-block">
                    <div>Signature et date suivi de la mention "lu et approuvé"<div>
                    <hr>
                </div>"""
    else :
        signature_patient_bloc = ""
    # --- 3. Préparation des données ---
    NOM_PAYEUR = f"{patient.nom_facturation if patient.nom_facturation else patient.nom}"
    ADRESSE_PAYEUR = patient.adresse if patient.adresse else ""
    VILLE_PAYEUR = f"{patient.ville}" if patient.ville else ""
    
    DATE_EMISSION_STR = format_date_fr(datetime.now())
    DATE_ECHEANCE = format_date_fr(datetime.now() + constantes_manager.get_constante("DELAI_PAIEMENT_FACTURE_DAYS") * timedelta(days=1))
    
    # Calcul des données du tableau
    lignes_data = []
    total_amount = 0.0

    # --- 4. Génération des lignes HTML du tableau ---
    trs_html = ""
    for acte in actes:
        type_rdv = TypeRDVService.get_type_by_id(acte.id_type_rdv)
        print(type_rdv)
        trs_html += f"""
        <tr>
            <td class="col-motif">{type_rdv.nom}</td>
            <td class="col-tarif-unitaire">{type_rdv.prix:.2f}</td>
            <td class="col-nombre">{acte.quantite:.0f}</td>
            <td class="col-prix-total">{(type_rdv.prix * acte.quantite):.2f} €</td>
        </tr>
        """
        total_amount += type_rdv.prix * acte.quantite

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

            /* --- LAYOUT HEADER (2 Colonnes) --- */
            .header-container {{
                display: flex;
                flex-direction: row;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 40px;
                width: 100%;
            }}

            /* --- COLONNE GAUCHE : Logo + Praticien --- */
            .left-column {{
                width: 45%;
                display: flex;
                flex-direction: column;
                align-items: flex-start;
            }}

            .logo-img {{
                width: 100px;
                height: auto;
            }}

            .practitioner-info {{
                font-size: 10pt important!;
                line-height: 1.4 important!;
            }}

            a{{ color: inherit; text-decoration: none; }}

            .practitioner-name {{
                font-weight: bold;
                font-size: 11pt;
                margin-bottom: 2px;
            }}

            /* --- COLONNE DROITE : Facture + Client --- */
            .right-column {{
                width: 45%;
                text-align: right;
            }}

            .facture-title {{
                font-weight: bold;
                font-size: 12pt;
                text-transform: uppercase;
                margin-bottom: 5px;
            }}

            .client-section {{
                margin-top: 30px;
                text-align: left;
                margin-left: auto;
                width: 60%;
                border: 3px solid #000;
                padding: 5px;
            }}

            .client-label {{ font-size: 9pt; margin-bottom: 2px; }}
            .client-nom {{ font-weight: bold; font-size: 11pt; }}

            /* --- CONTEXTE (Date / Patient) --- */
            .context-section {{
                margin-top: 20px;
                display: flex;
                justify-content: flex-end;
                margin-bottom: 40px;
            }}

            .context-table {{border-collapse: collapse;}}

            .context-table td {{
                padding: 2px 0 2px 15px;
                text-align: right;
            }}

            /* --- OBJET & TABLEAU --- */
            .objet-titre {{ font-weight: bold; margin-bottom: 5px; }}
            .objet-periode {{margin-bottom: 20px; font-size: 11pt; }}

            table.services {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}

            table.services td {{
                padding: 8px 5px;
                border-bottom: 1px solid #ccc;
                vertical-align: top;
                font-size: 10pt;
            }}

            .col-motif {{ width: 55%; text-align: left; }}
            .col-tarif-unitaire {{ width: 15%; text-align: center; }}
            .col-nombre {{ width: 15%; text-align: center; }}
            .col-prix-total {{ width: 15%; text-align: right; }}

            thead tr th {{border-bottom: 2px solid #000;}}

            .total-row td {{
                border-bottom: none;
                border-top: 1px solid #000;
                padding-top: 15px;
                font-weight: bold;
                font-size: 11pt;
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

            .signature-patient-block {{
                margin-top: 40px;
                float: left;
                width: 40%;
                text-align: left;
            }}

            /* --- FOOTER (Fixe & Bas) --- */
            .footer-legal {{
                position: fixed;
                /* MODIFICATION : Utilisation d'une valeur négative pour descendre dans la marge */
                bottom: -80px; 
                left: 0; 
                right: 0;
                text-align: center;
                font-size: 8pt;
                color: #000;
                line-height: 1.4;
                padding-bottom: 0px;
                background-color: white;
            }}

        </style>
    </head>
    <body>

        <div class="header-container">
            
            <div class="left-column">
                    {logo_img_tag}
                
                <div class="practitioner-info">
                    <div class="practitioner-name">{PRACTITIONER_NAME}</div>
                    <div>Cabinet d'ergothérapie NALAM</div>
                    <div>{CABINET_ADDRESS}</div>
                    <div>{PRACTITIONER_PHONE}</div>
                    <div><a href="mailto:{PRACTITIONER_EMAIL}">{PRACTITIONER_EMAIL}</a></div>
                </div>
            </div>

            <div class="right-column">
                <div class="facture-title">DEVIS {devis.id}</div>
                <div style="font-style: italic; font-size: 9pt; margin-top:5px;">Devis valable pendant {VALIDITE_DEVIS_DAYS} jours</div>
                
                <div class="client-section">
                    <div class="client-label">A l'attention de :</div>
                    <div class="client-nom">{NOM_PAYEUR}</div>
                    <div>{ADRESSE_PAYEUR}</div>
                    <div>{VILLE_PAYEUR}</div>
                </div>
            </div>
        </div>

        <div class="context-section">
            <table class="context-table">
                <tr>
                    <td>A Plaisir, le</td>
                    <td>{DATE_EMISSION_STR}</td>
                </tr>
                <tr>
                    <td>Patient :</td>
                    <td style="font-weight: bold;">{patient.prenom} {patient.nom}</td>
                </tr>
            </table>
        </div>

        <div class="objet-titre" style="color : #AFCFBE">Devis d'actes en ergothérapie concernant la periode :</div>
        <div class="objet-periode">{"Du "+ format_date_fr(devis.date_debut)} au {format_date_fr(devis.date_fin)}</div>

        <table class="services">
            <thead>
                <tr>
                    <th class="col-motif">Motif</th>
                    <th class="col-tarif-unitaire">Tarif Unitaire</th>
                    <th class="col-nombre">Nombre de séances</th>
                    <th class="col-prix-total">Prix Total</th>
                </tr>
            </thead>
            <tbody>
                {trs_html}
                <tr class="total-row">
                    <td colspan="2"></td>
                
                    <td style="text-align: right;">Total :</td>
                    <td style="text-align: right;">{total_amount:.2f} €</td>
                </tr>
            </tbody>
        </table>

        <div class="signature-block">
            <div style="margin-bottom: 5px;">{PRACTITIONER_NAME.upper()}</div>
            {signature_img_tag}
        </div>
        {signature_patient_bloc}
        

        <div class="footer-legal">
            <div>Profession inscrite au livre IV du code de la Santé Publique Loi n° 95-116 du 4 février 1995</div>
            <div>TVA non applicable, article 261 du code général des impôts (CGI).</div>
            <div>Conformément à la loi 92-1442 du 31/12/92, toute somme due non versée à l'échéance<br>supportera des pénalités de retard égales à 3 fois le taux d'intérêt légal.</div>
            <div style="margin-top: 5px;">Siret : {SIRET} &nbsp;&nbsp; APE {APE} &nbsp;&nbsp; RPPS : {ADELI}</div>
        </div>

    </body>
    </html>
    """

    return html_content

def generate_devis_pdf(html_content: str) -> bytes:
    
    pdf = HTML(string=html_content).write_pdf()
    return pdf

def save_devis_pdf(pdf_bytes: bytes, save_path:str ,filename: str) -> None:
    abs_dir = path.abspath(save_path)
    if not path.exists(abs_dir):
        makedirs(abs_dir)
    abs_file = path.join(abs_dir, filename)
    with open(abs_file, 'wb') as f:
        f.write(pdf_bytes)


def create_and_save(devis: Devis, actes:list[ActeDevis], patient: Patient, save_path: str, open_files :bool = False) -> str:
    html_content = generate_devis_html(devis, patient, actes)
    pdf = generate_devis_pdf(html_content)
    try : 
        with open(save_path, 'wb') as f:
            f.write(pdf)
        if open_files:
            import webbrowser
            webbrowser.open(save_path)
        return save_path
    
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du devis : {str(e)}")
        raise RegleMetierException(f"Erreur lors de la sauvegarde du devis : {str(e)}")