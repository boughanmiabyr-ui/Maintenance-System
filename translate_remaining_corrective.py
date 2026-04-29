"""
Translate remaining French corrective maintenance tasks (second batch)
"""

import os

REMAINING_TRANSLATIONS = {
    "Réglage roue de mesure": "Adjust measurement wheel",
    "Changement axe d'encodeur": "Change encoder shaft",
    "Changement tole bloc d'arret": "Change stop block plate",
    "Réglage tandeur": "Adjust tensioner",
    "Rincage+centrage IMS": "Rinse and center IMS",
    "Réglage K26": "Adjust K26",
    "Centrage d'applicateur seal": "Center seal applicator",
    "Ajustement tete d'insertion": "Adjust insertion head",
    "Réglage variation denudage": "Adjust stripping variation",
    "Réglage vé de centrage": "Adjust centering V-block",
    "Réparation tole bloc d'arrét": "Repair stop block plate",
    "Réglage enrouleur papier": "Adjust paper reel",
    "Réglage bras de pivotement coté 1": "Adjust pivot arm side 1",
    "Réglage bras de pivotement coté 2": "Adjust pivot arm side 2",
    "Réglage convoyeur": "Adjust conveyor",
    "Réglage goulette retractable": "Adjust retractable chute",
    "Changement Barrage photoelectrique d'enrouleur papier": "Change paper reel photoelectric barrier",
    "Réglage MCD": "Adjust MCD",
}

file_path = "app/routes/main.py"

print("Loading file...")
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content

print(f"Applying {len(REMAINING_TRANSLATIONS)} additional translations...")
# Apply translations (longer strings first)
sorted_translations = sorted(REMAINING_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True)
for french, english in sorted_translations:
    content = content.replace(f"'name': '{french}'", f"'name': '{english}'")

if content != original_content:
    print("Writing updated file...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Successfully translated remaining {len(REMAINING_TRANSLATIONS)} task names!")
else:
    print("No changes made")
