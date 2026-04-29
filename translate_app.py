"""
Comprehensive script to translate the entire application from French to English
"""

import os
import re
from pathlib import Path

# Create translation dictionary for common terms
TRANSLATIONS = {
    # Headers and Labels
    "N° de série": "Serial Number",
    "Date d'exécution": "Execution Date",
    "Points à contrôler": "Inspection Points",
    "Critère de jugement": "Acceptance Criteria",
    "Temps (min)": "Time (min)",
    "Remarques": "Remarks",
    "Tâche": "Task",
    "Critère": "Criteria",
    "N°": "No.",
    "Action": "Action",
    
    # Maintenance Report Headers
    "Rapport de Maintenance Corrective": "Corrective Maintenance Report",
    "Rapport de Préventive": "Preventive Maintenance Report",
    "Statut du rapport": "Report Status",
    "Date de rapport": "Report Date",
    "Statut": "Status",
    
    # Preventive Maintenance Tasks (Monthly) - 29 tasks
    "État des accessoires": "Accessories condition",
    "Bon état": "Good condition",
    "Purge du conditionneur": "Conditioner purge",
    "Contrôler câble": "Check cable",
    "Pas d'usure": "No wear",
    "Mobilité roulements": "Bearing mobility",
    "Aucun bruit": "No noise",
    "Usure courroies": "Belt wear",
    "Nettoyage roue encodeur": "Encoder wheel cleaning",
    "Aucune bavure": "No burrs",
    "Mobilité pinces": "Gripper mobility",
    "Aucun coincement": "No jamming",
    "État des couteaux": "Blade condition",
    "Tension courroie": "Belt tension",
    "0,35 mm": "0.35 mm",
    "Ventilateur coffret": "Cabinet fan",
    "Fonctionnel": "Functional",
    "Position bras pivotement": "Arm pivot position",
    "Alignement correct": "Correct alignment",
    "Pression manomètre": "Gauge pressure",
    "Valeurs normales": "Normal values",
    "Étalonnage presses": "Press calibration",
    "Cycle complet": "Complete cycle",
    "Paramètres TOP WIN": "TOP WIN parameters",
    "Désactivé": "Disabled",
    "Air comprimé": "Compressed air",
    "Air sec uniquement": "Dry air only",
    "Mouvement redressement": "Straightening movement",
    "Facile": "Easy",
    "Réglage unité dressage": "Dressing unit adjustment",
    "Correct": "Correct",
    "Déplacement bras": "Arm movement",
    "Griffes de serrage": "Clamping claws",
    "Fixe": "Fixed",
    "Vérification longueur": "Length verification",
    "Tolérance ±4mm": "Tolerance ±4mm",
    "Niveau d'huile": "Oil level",
    "Entre min et max": "Between min and max",
    "Lubrification bras": "Arm lubrication",
    "État coupe bande": "Band cutting condition",
    "Nettoyage crémaillère": "Rack cleaning",
    "Appareils pose bouchons": "Cork cap placement devices",
    "Bloc entraînement câble": "Cable drive block",
    "Roulements rouleaux": "Roller bearings",
    "Alignement OK": "Alignment OK",
    
    # Semi-Annual Tasks
    "Nettoyage armoire électrique": "Electrical cabinet cleaning",
    "Propre": "Clean",
    "Graissage capot": "Hood greasing",
    "Mouvement facile": "Easy movement",
    "Contrôle corrosion": "Corrosion check",
    "Aucune fuite": "No leaks",
    "Bandes transporteuses": "Conveyor belts",
    "Station seal": "Sealing station",
    "Fonctionnelle": "Functional",
    
    # UI Elements
    "Observation Technicien": "Technician Observations",
    "Nettoyage / Cleaning": "Cleaning",
    "Description de la tâche": "Task Description",
    "Task Description / Description de la tâche": "Task Description",
    "Points à contrôler / Inspection Points": "Inspection Points",
    "Instructions:": "Instructions:",
    "Sélectionner": "Select",
    "Rechercher": "Search",
    
    # Report sections
    "Monthly Preventive Systematic Maintenance": "Monthly Preventive Systematic Maintenance",
    "Semi-Annual Preventive Systematic Maintenance": "Semi-Annual Preventive Systematic Maintenance",
    "Corrective Maintenance": "Corrective Maintenance",
    "Mécanique": "Mechanical",
    "Électrique": "Electrical",
    "Hydraulique": "Hydraulic",
    "Pneumatique": "Pneumatic",
}

def translate_file(file_path):
    """Translate a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply translations (longer strings first to avoid partial replacements)
        sorted_translations = sorted(TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True)
        for french, english in sorted_translations:
            content = content.replace(french, english)
        
        # If content changed, write it back
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Translated: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error translating {file_path}: {str(e)}")
        return False

# Files to translate
files_to_translate = [
    "app/templates/maintenance_report_card.html",
    "app/templates/maintenance_report_card_old.html",
    "app/templates/corrective_maintenance_tasks.html",
    "app/templates/preventive_maintenance/report_form.html",
    "app/templates/preventive_maintenance/report_pdf.html",
    "app/templates/maintenance/report_pdf.html",
    "app/routes/preventive_maintenance.py",
    "app/routes/main.py",
]

print("Starting translation process...")
print("=" * 60)

translated_count = 0
for file_rel_path in files_to_translate:
    file_path = os.path.join(os.getcwd(), file_rel_path)
    if os.path.exists(file_path):
        if translate_file(file_path):
            translated_count += 1
    else:
        print(f"⚠ File not found: {file_path}")

print("=" * 60)
print(f"Translation completed! {translated_count} files translated.")
