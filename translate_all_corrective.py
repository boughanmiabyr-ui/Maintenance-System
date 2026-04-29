"""
Complete translation of ALL corrective maintenance tasks in main.py
"""

import os

# All French to English translations for corrective tasks (comprehensive list)
ALL_CORRECTIVE_TRANSLATIONS = {
    # Existing ones (already partially translated - fixing to ensure consistency)
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
    
    # Additional mechanical (not yet translated)
    "Changement vérin tole de guidage": "Change guide plate cylinder",
    "Changement appui cpl": "Change CPL support",
    "Changement levier de fixation": "Change fixing lever",
    "Changement manchon de fixation outil": "Change tool fixing sleeve",
    "Changement coupe bande": "Change band cutter",
    "Changement lame de coupe bande": "Change band cutting blade",
    "Changement boitier de coupe bande": "Change band cutter housing",
    "Changement joint de coupe bande": "Change band cutter joint",
    "Changement piston de coupe bande": "Change band cutter piston",
    "Changement galet devant": "Change front roller",
    "Changement galet en arriére": "Change rear roller",
    "Changement palque devant": "Change front plate",
    "Changement plaque en arriére": "Change rear plate",
    "Changement vibreur": "Change vibrator",
    "Changement mondrin": "Change chuck",
    "Changement dornpin": "Change dornpin",
    "Ajustement Touniquer": "Adjust Touniquer",
    "Ajustement tete d'insertion": "Adjust insertion head",
    "Ajustement coupe Bande": "Adjust band cutter",
    "Réparation tole bloc d'arrét": "Repair stop block plate",
    "Changement insertion sleeve": "Change insertion sleeve",
    "Changement manchant seal": "Change seal sleeve",
    "Ajustement bande transporteuse": "Adjust conveyor belt",
    "Remplacement Joint double station seal": "Replace double joint sealing station",
    
    # Electrical (not yet translated)
    "Ajustement micro switch": "Adjust micro switch",
    "Changement ACS116 (servomoteur)": "Change ACS116 (servomotor)",
    "Changement capteur des machoires": "Change gripper sensor",
    "Changement capteur mouvement linéaire": "Change linear movement sensor",
    "Changement capteur mouvement rotationnelle": "Change rotational movement sensor",
    "Changement ACS108": "Change ACS108",
    "Changement détecteur optique tole de guidage": "Change optical detector guide plate",
    "Changement Barrage photoelectrique d'enrouleur papier": "Change paper reel photoelectric barrier",
    "Ajustement capteur bras de pivotement coté 1": "Adjust pivot arm sensor side 1",
    "Ajustement capteur bras de pivotement coté 2": "Adjust pivot arm sensor side 2",
    "Changement capteur de présence seal": "Change seal presence sensor",
    "Changement capteur goulette retractable": "Change retractable chute sensor",
    "Changement ACS204 (servomoteur)": "Change ACS204 (servomotor)",
    "Changement cable MCI rg 45": "Change MCI RG45 cable",
    "Changement cable capteur": "Change sensor cable",
    
    # IT/Software (not yet translated)
    "Ajustement et calibrage SQC": "Adjust and calibrate SQC",
    "Changement encodeur": "Change encoder",
    "Changement moteur": "Change motor",
    "Changement variateur vitesse": "Change speed driver",
    "Remplacement  circuit imprimé": "Replace printed circuit",
    "Changement contacteur": "Change contactor",
    "Changement relais": "Change relay",
    "Remplacement prise électrique": "Replace electrical outlet",
    "Changement câble d'alimentation": "Change power cable",
    "Remplacement sectionneur": "Replace disconnector",
}

file_path = "app/routes/main.py"

print("Loading file...")
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content

print(f"Applying {len(ALL_CORRECTIVE_TRANSLATIONS)} translations...")
# Apply translations (longer strings first to avoid partial replacements)
sorted_translations = sorted(ALL_CORRECTIVE_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True)
for french, english in sorted_translations:
    content = content.replace(f"'name': '{french}'", f"'name': '{english}'")

# Check if changes were made
if content != original_content:
    print("Writing updated file...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Successfully translated ALL corrective maintenance tasks!")
    
    # Count changes for verification
    changes = sum(1 for f, e in sorted_translations if f"'name': '{f}'" in original_content)
    print(f"✓ Translated {changes} task names to English")
else:
    print("No changes made - all tasks may already be translated")
