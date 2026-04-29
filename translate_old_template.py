"""
Translate remaining French content in maintenance_report_card_old.html
"""

import os

REMAINING_TRANSLATIONS_OLD = {
    "Maintenance préventive systématique semestrielle": "Semi-Annual Systematic Preventive Maintenance",
    "Observations générales et conclusions": "General Observations and Conclusions",
    "Observations générales et conclusions": "General Observations and Conclusion",
    "Overall Findings & Observations / Observations générales et conclusions": "Overall Findings & Observations",
    "Machine Condition / État de la machine": "Machine Condition",
    "Nécessite réparation (Requires Repair)": "Requires Repair",
    "Issues Found / Problèmes détectés": "Issues Found",
    "Vérifier la mobilité des pinces (grippers)": "Check gripper mobility",
    "Vérifier l'état des couteaux": "Check blade condition",
    "Contrôler les connexions électriques": "Check electrical connections",
    "Vérifier les filtres et les remplacer si nécessaire": "Check filters and replace if necessary",
    "Contrôler le système de refroidissement": "Check cooling system",
    "Vérifier l'état des tubes et des tuyaux": "Check condition of tubes and pipes",
    "Vérifier les contacts et les relais électriques": "Check electrical contacts and relays",
    "Contrôler les câbles et les connexions": "Check cables and connections",
    "Vérifier les capteurs et les détecteurs": "Check sensors and detectors",
    "Contrôler l'isolation électrique": "Check electrical insulation",
    "Sécurité / Safety": "Safety",
    "Vérifier le fonctionnement des dispositifs de sécurité": "Check safety device operation",
    "Vérifier les roulements à bille": "Check ball bearings",
    "Contrôler les joints et les étanchéités": "Check joints and seals",
    "Étanchéité / Sealing": "Sealing",
    "Vérifier l'usure des chaînes": "Check chain wear",
}

file_path = "app/templates/maintenance_report_card_old.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content

# Apply translations (longer strings first to avoid partial replacements)
sorted_translations = sorted(REMAINING_TRANSLATIONS_OLD.items(), key=lambda x: len(x[0]), reverse=True)
for french, english in sorted_translations:
    content = content.replace(french, english)

# Write back if changed
if content != original_content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Translated remaining French content in {file_path}")
else:
    print(f"No changes made to {file_path}")
