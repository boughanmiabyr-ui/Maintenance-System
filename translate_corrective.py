"""
Additional translation for corrective maintenance tasks (all 67 items in main.py)
"""

import os
from pathlib import Path

# French to English translation for corrective maintenance tasks
CORRECTIVE_TRANSLATIONS = {
    # Mechanical Tasks (French -> English)
    "Changement oreil a collet enduit": "Change fitted collar ear",
    "Ajustement unité redressement": "Adjust straightening unit",
    "Changement galet": "Change roller",
    "Ajustement wire drive": "Adjust wire drive",
    "Changement courroies crantées": "Change toothed belts",
    "Changement roue de mesure": "Change measurement wheel",
    "Changement roues dentées (Z32)": "Change toothed wheels (Z32)",
    "Changement roues dentées (Z18)": "Change toothed wheels (Z18)",
    "Changement galet de pression": "Change pressure roller",
    "Changement capot de protection": "Change protective cover",
    "Changement guide cable": "Change cable guide",
    "Changement axe d'encodeur": "Change encoder shaft",
    "Changement roullement rainurée": "Change grooved bearing",
    "Ajustement des machoires": "Adjust jaws",
    "Changement machoires": "Change jaws",
    "Changement Pivotement CPL": "Change Pivot CPL",
    "Changement lames a dénudés": "Change stripping blades",
    "Changement lames de coupe": "Change cutting blades",
    "Ajustement tete de coupe": "Adjust cutting head",
    "Changement tole bloc d'arret": "Change stop block plate",
    "Changemnt tole de guidage (vé de centrage)": "Change centering guide plate (V-centering)",
    "Réglage tapis transporteuse": "Adjust conveyor belt",
    "Centrage d'applicateur seal": "Center seal applicator",
    "Changement manchon ressort": "Change spring sleeve",
    "Changement pignon": "Change pinion",
    "Changement chaîne transmission": "Change transmission chain",
    "Changement micro switch": "Change micro switch",
    "Changement capteur": "Change sensor",
    "Remplacement liaison rotative": "Replace rotary joint",
    "Changement pompe hydraulique": "Change hydraulic pump", 
    
    # Electrical Tasks
    "Changement encodeur": "Change encoder",
    "Changement moteur": "Change motor",
    "Changement variateur vitesse": "Change speed driver",
    "Remplacement  circuit imprimé": "Replace printed circuit",
    "Changement contacteur": "Change contactor",
    "Changement relais": "Change relay",
    "Remplacement prise électrique": "Replace electrical outlet",
    "Changement câble d'alimentation": "Change power cable",
    "Remplacement sectionneur": "Replace disconnector",
    
    # Hydraulic Tasks  
    "Changement tuyau hydraulique": "Change hydraulic hose",
    "Remplacement filtre hydraulique": "Replace hydraulic filter",
    "Changement vanne solenoide": "Change solenoid valve",
    "Remplacement joint oring": "Replace O-ring",
    "Vidange huile hydraulique": "Drain hydraulic oil",
    "Nettoyage radiateur hydraulique": "Clean hydraulic radiator",
    "Changement manomètre hydraulique": "Change hydraulic pressure gauge",
    "Remplacement accumulateur": "Replace accumulator",
    "Changement distributeur hydraulique": "Change hydraulic distributor",
    
    # Pneumatic Tasks
    "Changement tuyau pneumatique": "Change pneumatic hose",
    "Remplacement filtre air comprimé": "Replace compressed air filter",
    "Changement réducteur pression": "Change pressure reducer",
    "Remplacement électrovanne pneumatique": "Replace pneumatic solenoid valve",
    "Changement vérin pneumatique": "Change pneumatic cylinder",
    "Vidange reservoir air": "Drain air reservoir",
    "Nettoyage filtre compresseur": "Clean compressor filter",
    "Changement détendeur air": "Change air regulator",
    "Remplacement tube air comprimé": "Replace compressed air tube",
}

def translate_corrective_file(file_path):
    """Translate corrective maintenance tasks in main.py"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply translations for corrective items
        for french, english in CORRECTIVE_TRANSLATIONS.items():
            content = content.replace(f"'name': '{french}'", f"'name': '{english}'")
        
        # If content changed, write it back
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Translated corrective tasks: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"✗ Error translating {file_path}: {str(e)}")
        return False

# Translate corrective maintenance file
file_path = "app/routes/main.py"
if os.path.exists(file_path):
    if translate_corrective_file(file_path):
        print("\nAll corrective maintenance tasks translated to English!")
    else:
        print("No changes made - corrective tasks may already be translated")
else:
    print(f"File not found: {file_path}")
