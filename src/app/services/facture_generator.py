from datetime import timedelta, datetime
from weasyprint import HTML
from os import path, environ, makedirs
from sys import path as sys_path
from base64 import b64encode
import traceback
# Import des modèles existants
from app.model.facture import Facture
from app.model.patient import Patient
from app.model.ligneFacture import LigneFacture
from app.model.typeRDV import TypeRDV
from app.model.rendezVous import RendezVous
sys_path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))) or '.')
from app.services import constantes_manager

def format_date_fr(date_obj):
    """Transforme une date datetime en chaîne française (ex: 13 janvier 2024)"""
    if not date_obj: return ""
    mois = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai", 6: "juin",
        7: "juillet", 8: "août", 9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
    }
    return f"{date_obj.day} {mois[date_obj.month]} {date_obj.year}"

def generate_facture_html(facture: Facture, patient: Patient, lignes: list[LigneFacture], annulation_factures: list[str], date_debut: datetime, date_fin: datetime) -> bytes:
    # --- 1. Chargement des constantes ---
    PRACTITIONER_NAME = constantes_manager.get_constante("PRACTITIONER_NAME") 
    PRACTITIONER_PHONE = constantes_manager.get_constante("PRACTITIONER_PHONE") 
    CABINET_ADDRESS = constantes_manager.get_constante("CABINET_ADDRESS") 
    PRACTITIONER_EMAIL = constantes_manager.get_constante("PRACTITIONER_EMAIL") 
    SIRET = constantes_manager.get_constante("SIRET") 
    APE = constantes_manager.get_constante("APE") 
    ADELI = constantes_manager.get_constante("ADELI")

    # --- 2. Gestion du Logo ---
    logo_file = path.join(environ.get("APPDATA"),"CabiLib", 'logo.png').replace('\\', '/')
    logo_base64 = ''
    print("Logo file path:", logo_file)
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
    print("Signature file path:", signature_file)
    try:
        with open(signature_file, 'rb') as img_f:
            signature_bytes = img_f.read()
            signature_base64 = b64encode(signature_bytes).decode('utf-8')
    except Exception:
        traceback.print_exc()
        signature_base64 = ''
    
    signature_img_tag = f'<img src="data:image/jpeg;base64,{signature_base64}" class="signature-img" alt="Signature" />' if signature_base64 else ''
    
    # --- 3. Préparation des données ---
    NOM_PAYEUR = f"{patient.nom_facturation if patient.nom_facturation else patient.nom}"
    ADRESSE_PAYEUR = patient.adresse if patient.adresse else ""
    VILLE_PAYEUR = f"{patient.ville}" if patient.ville else ""
    
    DATE_EMISSION_STR = format_date_fr(facture.date_emission)
    DATE_ECHEANCE = format_date_fr(facture.date_emission + constantes_manager.get_constante("DELAI_PAIEMENT_FACTURE_DAYS") * timedelta(days=1))
    
    # Calcul des données du tableau
    lignes_data = []
    total_amount = 0.0

    for ligne in lignes:
        total_amount += ligne.montant_facture
        # Note: Gestion d'erreur si getRendezVousById retourne une liste vide
        rendez_vous = RendezVous.getRendezVousById(ligne.rdv_id)
        
        if rendez_vous:
            typeRDV = TypeRDV.getTypeRDVById(rendez_vous.type_id)
            description = f"{typeRDV.nom}" if typeRDV else "Séance"
            
            lignes_data.append({
                "description": description,
                "date": format_date_fr(rendez_vous.date),
                "prix": f"{ligne.montant_facture:.2f} €"
            })

    # Texte Période
    texte_periode = f"Du {format_date_fr(date_debut)} au {format_date_fr(date_fin)}"

    # Annulation
    annulation_block = ""
    if (annulation_factures is not None and annulation_factures != []):
        print(annulation_factures)
        cancelled_list = ", ".join(annulation_factures)
        label = "Annule et remplace la facture :" if len(annulation_factures) == 1 else "Annule et remplace les factures :"
        annulation_block = f"""
        <div class="annulation-box">
            <span class="rouge-gras">{label}</span><br>
            <span class="rouge-normal">{cancelled_list}</span>
        </div>
        """

    # --- 4. Génération des lignes HTML du tableau ---
    trs_html = ""
    for item in lignes_data:
        trs_html += f"""
        <tr>
            <td class="col-desc">{item['description']}</td>
            <td class="col-date">le {item['date']}</td>
            <td class="col-prix">{item['prix']}</td>
        </tr>
        """

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

            .annulation-box {{
                border: 1px solid #cc0000;
                padding: 5px;
                margin-bottom: 10px;
                font-size: 9pt;
                text-align: left;
                background-color: #fff0f0;
                display: inline-block;
                width: 100%;
                box-sizing: border-box;
            }}
            .rouge-gras {{ color: #cc0000; font-weight: bold; }}
            .rouge-normal {{ color: #cc0000; }}

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
            .context-table {{
                border-collapse: collapse;
            }}
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
            .col-desc {{ width: 55%; text-align: left; }}
            .col-date {{ width: 25%; text-align: left; }}
            .col-prix {{ width: 20%; text-align: right; }}

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
                <div class="facture-title">FACTURE {facture.id}</div>
                {annulation_block}
                <div style="font-style: italic; font-size: 9pt; margin-top:5px;">A régler avant le {DATE_ECHEANCE}</div>
                
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

        <div class="objet-titre">Rééducation en ergothérapie correspondant à la période :</div>
        <div class="objet-periode">{texte_periode}</div>

        <table class="services">
            <tbody>
                {trs_html}
                <tr class="total-row">
                    <td></td>
                    <td style="text-align: right;">Total :</td>
                    <td style="text-align: right;">{total_amount:.2f} €</td>
                </tr>
            </tbody>
        </table>

        <div class="signature-block">
            <div style="margin-bottom: 5px;">{PRACTITIONER_NAME.upper()}</div>
            {signature_img_tag}
        </div>

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

def generate_facture_pdf(html_content: str) -> bytes:
    
    pdf = HTML(string=html_content).write_pdf()
    return pdf

def save_facture_pdf(pdf_bytes: bytes, save_path:str ,filename: str) -> None:
    abs_dir = path.abspath(save_path)
    if not path.exists(abs_dir):
        makedirs(abs_dir)
    abs_file = path.join(abs_dir, filename)
    with open(abs_file, 'wb') as f:
        f.write(pdf_bytes)

def create_and_save (facture: Facture, patient: Patient, lignes: list[LigneFacture], annulation_factures: list[str], date_debut: datetime, date_fin: datetime) -> str:
    html_content = generate_facture_html(facture, patient, lignes, annulation_factures, date_debut, date_fin)
    pdf = generate_facture_pdf(html_content)
    filename = f"{facture.id}.pdf"
    basepath = constantes_manager.get_constante("FACTURES_DIR")
    fac_path = facture.date_emission.strftime("%Y-%m")
    save_facture_pdf(pdf, path.join(basepath, fac_path), filename)
    return path.join(basepath, fac_path, filename)