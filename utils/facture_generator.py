
from datetime import timedelta
from weasyprint import HTML, CSS
import os
from app.model.facture import Facture
from app.model.patient import Patient
from app.model.ligneFacture import LigneFacture
from app.model.typeRDV import TypeRDV
from app.model.rendezVous import RendezVous
# Ajout : import des constantes pour l'en-tête
import sys
import base64
import importlib
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) or '.')
from utils import constantes_manager

def generate_facture_pdf(facture: Facture, patient: Patient, lignes: list[LigneFacture], annulation_factures: list[str]) -> bytes:
    # Recharge dynamiquement les constantes (comme dans votre code original)
    PRACTITIONER_NAME = constantes_manager.get_constante("PRACTITIONER_NAME") 
    PRACTITIONER_PHONE = constantes_manager.get_constante("PRACTITIONER_PHONE") 
    CABINET_ADDRESS = constantes_manager.get_constante("CABINET_ADDRESS") 
    PRACTITIONER_EMAIL = constantes_manager.get_constante("PRACTITIONER_EMAIL") 
    SIRET = constantes_manager.get_constante("SIRET") 
    APE = constantes_manager.get_constante("APE") 
    ADELI = constantes_manager.get_constante("ADELI")

    # (Votre code d'encodage du logo en base64)
    logo_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logo.png')
    logo_base64 = ''
    try:
        with open(logo_file, 'rb') as img_f:
            logo_bytes = img_f.read()
            logo_base64 = base64.b64encode(logo_bytes).decode('utf-8')
    except Exception:
        logo_base64 = ''

    logo_img_tag = f'<img src="data:image/png;base64,{logo_base64}" class="logo-stack" alt="Logo Cabinet" />' if logo_base64 else ''
    
    # Simuler les informations du payeur / tuteur
    NOM_PAYEUR = "M. & Mme NOSMAS SOUBESTE" # Variable à définir dans votre logique
    ADRESSE_PAYEUR = "6 rue du vieux moulin" # Variable à définir dans votre logique
    VILLE_PAYEUR = "78370 PLAISIR" # Variable à définir dans votre logique
    
    # Date d'échéance (à calculer dans votre logique)
    DATE_ECHEANCE = (facture.date_emission + timedelta(days=10)).strftime('%d %B %Y') # Exemple
    
    total_amount = 0
    lignes_html = ""
    for ligne in lignes:
        total_amount += ligne.montant_facture
        rendez_vous = RendezVous.getRendezVousById(ligne.rdv_id)
        type_id = rendez_vous.type_id
        typeRDV = TypeRDV.getTypeRDVById(type_id)
        
        # Le modèle utilise un format de ligne: Description | Date | Prix

        description = f"{typeRDV.nom} ({typeRDV.duree} min)"

        lignes_html += f"""
            <tr class="line-item">
                <td class="description">{description}</td>
                <td class="date">le {rendez_vous.date.strftime('%d %B %Y')}</td>
                <td class="price">{typeRDV.prix:.2f} €</td>
            </tr>"""
    
    # Ajout des lignes vides ou fantômes du modèle pour la cohérence
    lignes_html += """
            <tr class="line-item"><td></td><td></td><td></td></tr>
            <tr class="line-item"><td></td><td></td><td></td></tr>"""
            
    # --- DÉBUT DE LA LOGIQUE D'ANNULATION ET REMPLACEMENT ---
    annulation_tag = ""
    if annulation_factures:
        # Formatte la liste des factures annulées
        cancelled_invoices_list = ", ".join(annulation_factures)
        # Construit la balise HTML pour l'affichage
        if (len(annulation_factures) == 1):

            annulation_tag = f"""
            <p class="annulation-tag">
                Annule et remplace la facture: <span class="cancelled-list">{cancelled_invoices_list}</span>
            </p>
            """
        elif (len(annulation_factures) > 1):
            annulation_tag = f"""
            <p class="annulation-tag">
                Annule et remplace les factures: <span class="cancelled-list">{cancelled_invoices_list}</span>
            </p>
            """
    # --- FIN DE LA LOGIQUE D'ANNULATION ET REMPLACEMENT ---


    html_content = f"""
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 40px; }}
            body {{ font-family: Arial, sans-serif; font-size: 11pt; }}
            
            /* --- Style de l'En-tête --- */
            .header-container {{ display: flex; align-items: flex-start; margin-bottom: 20px; }}
            
            /* Logo NALAM (Bloc gauche) */
            .logo-block {{ 
                display: flex; 
                flex-direction: column; 
                align-items: center; 
                margin-right: 20px;
                height: 200px; /* Hauteur pour aligner le texte vertical */
            }}
            .vertical-text {{
                writing-mode: vertical-rl;
                transform: rotate(180deg);
                font-size: 18pt;
                font-weight: bold;
                letter-spacing: 5px;
                padding-right: 5px;
            }}
            .logo-stack {{ width: 80px; height: auto; margin-bottom: 5px; }}
            
            /* Info Praticien (Bloc central) */
            .practitioner-info {{ width: 50%; }}
            .facture-details {{ width: 40%; text-align: right; }}

            /* Style pour Annulation et Remplacement */
            .annulation-tag {{
                margin: 0;
                font-size: 10pt;
                color: #cc0000; /* Rouge ou couleur de distinction */
                font-weight: bold;
                margin-top: 5px; /* Petit espace après le numéro de facture */
            }}
            .cancelled-list {{
                font-weight: normal; /* Optionnel : pour mettre en valeur les numéros de facture */
            }}
            
            /* Info Facture/Payeur */
            .facture-meta {{ margin-top: 10px; margin-bottom: 30px; }}
            .meta-line {{ margin-bottom: 5px; font-size: 10pt; }}
            .meta-line strong {{ font-size: 12pt; }}
            
            .billing-info {{ margin-top: 20px; }}
            .billing-info p {{ margin: 0; line-height: 1.3; font-size: 11pt; }}
            .billing-info .attention {{ font-size: 10pt; font-weight: bold; margin-bottom: 5px; }}

            /* --- Tableau des services --- */
            .service-table {{ 
                width: 100%; 
                border-collapse: collapse;
                margin-top: 20px;
            }}
            .service-table td {{ 
                padding: 4px 0; 
                border-bottom: 1px solid #ccc; /* Séparateurs fins */
                vertical-align: top;
                height: 1.5em; /* Assure la hauteur des lignes vides */
                font-size: 11pt;
            }}
            .service-table .description {{ width: 50%; }}
            .service-table .date {{ width: 30%; text-align: left; }}
            .service-table .price {{ width: 20%; text-align: right; }}
            
            .total-row td {{ 
                border-bottom: none; 
                border-top: 1px solid #000;
                font-weight: bold;
                padding-top: 8px;
            }}
            .total-row .total-label {{ text-align: right; }}
            .total-row .total-amount {{ text-align: right; }}

            /* --- Pied de page --- */
            .footer-legal {{ 
                position: fixed; 
                bottom: 40px; 
                left: 40px; 
                right: 40px; 
                font-size: 8pt; 
                text-align: center; 
                border-top: 1px solid #ccc;
                padding-top: 10px;
            }}
            .signature-block {{
                position: absolute;
                bottom: 100px;
                right: 40px;
                text-align: center;
                font-size: 10pt;
            }}
        </style>
    </head>
    <body>
        <div class="header-container">
            <div class="logo-block">
                <span class="vertical-text">NALAM</span>
                {logo_img_tag}
            </div>
            
            <div class="practitioner-info">
                <h2 style="margin: 0; font-size: 14pt;">FACTURE {facture.id}</h2>
                {annulation_tag} <div class="meta-line">A régler avant le <strong>{DATE_ECHEANCE}</strong></div>
                
                <p style="margin-top: 20px; font-weight: bold; font-size: 12pt;">{PRACTITIONER_NAME}</p>
                <p style="margin: 0;">Cabinet d'ergothérapie NALAM</p>
                <p style="margin: 0;">{CABINET_ADDRESS}</p>
                <p style="margin: 0;">{PRACTITIONER_PHONE}</p>
                <p style="margin: 0;">{PRACTITIONER_EMAIL}</p>
            </div>
            
            <div class="facture-details">
                <div class="billing-info">
                    <p class="attention">A l'attention de :</p>
                    <p style="font-weight: bold;">{NOM_PAYEUR}</p>
                    <p>{ADRESSE_PAYEUR}</p>
                    <p>{VILLE_PAYEUR}</p>
                </div>
                
                <table style="width: 100%; margin-top: 30px;" class="noborder-table">
                    <tr>
                        <td style="text-align: right;">A Plaisir, le</td>
                        <td style="text-align: right;">{facture.date_emission.strftime('%d.%m.%Y')}</td>
                    </tr>
                    <tr>
                        <td style="text-align: right;">Patient:</td>
                        <td style="text-align: right; font-weight: bold;">{patient.prenom} {patient.nom}</td>
                    </tr>
                </table>
            </div>
        </div>

        <p style="margin-top: 20px; font-weight: bold;">Rééducation en ergothérapie correspondant au mois de :</p>
        <p style="font-size: 12pt;">{facture.periode_mois.upper() if hasattr(facture, 'periode_mois') else 'JANVIER'}</p>

        <table class="service-table">
            <tbody>
                {lignes_html}
                <tr class="total-row">
                    <td colspan="2" class="total-label">Total:</td>
                    <td class="total-amount">{total_amount:.2f} €</td>
                </tr>
            </tbody>
        </table>
        
        <div class="signature-block">
            <p>{PRACTITIONER_NAME}</p>
            <p style="border-top: 1px solid #000; padding-top: 5px;">SIGNATURE</p>
        </div>

        <div class="footer-legal">
            <p>Profession inscrite au livre IV du code de la Santé Publique Loi n 95-116 du 4 février 1995</p>
            <p>TVA non applicable, article 261 du code général des impôts (CGI).</p>
            <p>Conformément à la loi 92-1442 du 31/12/92, toute somme due non versée à l'échéance supportera des pénalités de retard égales à 3 fois le taux d'intérêt légal.</p>
            <p>Siret: {SIRET} APE {APE} ADELI: {ADELI}</p>
        </div>
        
    </body>
    </html>
    """

    # Generate PDF from HTML content
    pdf = HTML(string=html_content).write_pdf()

    return pdf

def save_facture_pdf(pdf_bytes: bytes, path:str ,filename: str) -> None:
    abs_dir = os.path.abspath(path)
    if not os.path.exists(abs_dir):
        os.makedirs(abs_dir)
    abs_file = os.path.join(abs_dir, filename)
    with open(abs_file, 'wb') as f:
        f.write(pdf_bytes)

def create_and_save (facture: Facture, patient: Patient, lignes: list[LigneFacture], annulation_factures: list[str]) -> str:
    pdf = generate_facture_pdf(facture, patient, lignes, annulation_factures)
    filename = f"{facture.id}.pdf"
    basepath = constantes_manager.get_constante("FACTURES_DIR")
    path = facture.date_emission.strftime("%Y-%m")
    save_facture_pdf(pdf, os.path.join(basepath, path), filename)
    return os.path.join(basepath, path, filename)