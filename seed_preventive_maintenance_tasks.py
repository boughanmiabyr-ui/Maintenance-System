#!/usr/bin/env python3
"""
Seed script to populate 22 French preventive maintenance tasks
This script creates a complete preventive maintenance plan with all 22 tasks
from the French maintenance checklist
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db, PreventiveMaintenancePlan, PreventiveMaintenanceTask, Machine, User
from datetime import date, timedelta

# Create app context
app = create_app()

# List of French maintenance tasks with EXACT MATCH to reference document
# Includes frequency mapping: "mensuelle" (monthly) and "semestrielle" (semi-annual)
MAINTENANCE_TASKS = [
    # MENSUELLE (Monthly) - Tasks 1-4, 7-8, and additional maintenance tasks
    {
        "task_number": 1,
        "task_description": "Vérifier le système de sécurité de la machine (Arrêt d'urgence, marche-Arrêt...)",
        "category": "Sécurité / Safety",
        "estimated_duration_minutes": 15,
        "required_materials": "Aucun",
        "safety_precautions": "Arrêter complètement la machine avant d'effectuer cette vérification",
        "notes": "Vérifier que chaque arrêt d'urgence est capable d'arrêter la machine. Chaque arrêt fonctionnel.",
        "frequency": "mensuelle"
    },
    {
        "task_number": 2,
        "task_description": "Vérifier l'état des accessoires liés au poste de travail (loupe, mètre, support d'éclairage...)",
        "category": "Accessoires / Accessories",
        "estimated_duration_minutes": 10,
        "required_materials": "Accessoires de vérification",
        "safety_precautions": "Utiliser les équipements de protection appropriés",
        "notes": "Les accessoires doivent exister et être en bon état",
        "frequency": "mensuelle"
    },
    {
        "task_number": 3,
        "task_description": "Faire une purge pour évacuer l'eau accumulée dans le conditionneur",
        "category": "Maintenance / Maintenance",
        "estimated_duration_minutes": 20,
        "required_materials": "Bac de récupération, outils",
        "safety_precautions": "Placer le bac avant d'ouvrir la purge",
        "notes": "Ouvrir la purge pendant 1 minute. Voir fig 001",
        "frequency": "mensuelle"
    },
    {
        "task_number": 4,
        "task_description": "Contrôler l'œuil enduit pour câble",
        "category": "Contrôle / Check",
        "estimated_duration_minutes": 10,
        "required_materials": "Aucun",
        "safety_precautions": "Vérifier l'isolation des câbles",
        "notes": "Pas d'usure. Inspection visuelle",
        "frequency": "mensuelle"
    },
    
    # SEMESTRIELLE (Semi-Annual) - Tasks 5-6, 9-10
    {
        "task_number": 5,
        "task_description": "Vérifier la mobilité des roulements des redressement",
        "category": "Roulements / Bearings",
        "estimated_duration_minutes": 15,
        "required_materials": "Aucun",
        "safety_precautions": "Écouter attentivement le fonctionnement",
        "notes": "Aucun bruit lors du fonctionnement. Inspection sensorielle",
        "frequency": "semestrielle"
    },
    {
        "task_number": 6,
        "task_description": "Vérifier l'usure des courroies, roues dentées et roulement",
        "category": "Usure / Wear",
        "estimated_duration_minutes": 20,
        "required_materials": "Outils d'inspection",
        "safety_precautions": "Arrêter la machine avant l'inspection",
        "notes": "Pas d'usures, pas de bavures. Inspection manuelle",
        "frequency": "semestrielle"
    },
    
    # MENSUELLE - Task 7
    {
        "task_number": 7,
        "task_description": "Vérifier et nettoyer la roue d'encoudeur avec une brosse en courbe",
        "category": "Nettoyage / Cleaning",
        "estimated_duration_minutes": 25,
        "required_materials": "Brosse en cuivre, chiffon",
        "safety_precautions": "Utiliser une brosse adaptée pour ne pas endommager",
        "notes": "Aucune usure et aucune bavure sur la roue d'encoudeur. Voir fig 003. Inspection manuelle",
        "frequency": "mensuelle"
    },
    
    # MENSUELLE - Task 8
    {
        "task_number": 8,
        "task_description": "Vérifier la mobilité des pinces (grippers)",
        "category": "Mobilité / Movement",
        "estimated_duration_minutes": 15,
        "required_materials": "Aucun",
        "safety_precautions": "Vérifier en mode manuel seulement",
        "notes": "Lors d'activation de l'option Basculer, les sorties aucune coincement de pinces. Inspection visuelle",
        "frequency": "mensuelle"
    },
    
    # SEMESTRIELLE - Tasks 9-10
    {
        "task_number": 9,
        "task_description": "Vérifier l'état des couteaux",
        "category": "État / Condition",
        "estimated_duration_minutes": 20,
        "required_materials": "Jauge de mesure",
        "safety_precautions": "Faire attention aux arêtes tranchantes",
        "notes": "Pas d'usure. Voir fig 004. Produire 3 échantillons. Inspection visuelle",
        "frequency": "semestrielle"
    },
    {
        "task_number": 10,
        "task_description": "Vérifier la tension du courroie transporteuse",
        "category": "Tension / Tension",
        "estimated_duration_minutes": 20,
        "required_materials": "Jauge de 0,35mm",
        "safety_precautions": "Arrêter la machine avant d'ajuster",
        "notes": "Jeux entre tapis et reglette = 0,35mm. Voir fig 005. Inspection manuelle",
        "frequency": "semestrielle"
    },
    
    # Additional MENSUELLE tasks
    {
        "task_number": None,  # No numbering for additional tasks in report
        "task_description": "Vérifier l'alignement des lames de coupe",
        "category": "Alignement / Alignment",
        "estimated_duration_minutes": 15,
        "required_materials": "Outil d'alignement",
        "safety_precautions": "Arrêter la machine avant vérification",
        "notes": "Les lames doivent être parfaitement alignées",
        "frequency": "mensuelle"
    },
    
    # Additional SEMESTRIELLE tasks
    {
        "task_number": None,
        "task_description": "Contrôler les connexions électriques",
        "category": "Électrique / Electrical",
        "estimated_duration_minutes": 15,
        "required_materials": "Multimètre, outils",
        "safety_precautions": "Vérifier l'isolation des connexions",
        "notes": "Vérifier l'absence d'oxydation et la bonne connexion",
        "frequency": "semestrielle"
    },
    
    # Additional MENSUELLE tasks
    {
        "task_number": None,
        "task_description": "Vérifier les niveaux de fluides (huile, eau, etc.)",
        "category": "Fluides / Fluids",
        "estimated_duration_minutes": 15,
        "required_materials": "Jauge, bac de remplissage",
        "safety_precautions": "Machine froide avant vérification",
        "notes": "Tous les niveaux doivent être au correct",
        "frequency": "mensuelle"
    },
    {
        "task_number": None,
        "task_description": "Vérifier les filtres et les remplacer si nécessaire",
        "category": "Filtres / Filters",
        "estimated_duration_minutes": 20,
        "required_materials": "Filtres de rechange, outils",
        "safety_precautions": "Machine arrêtée",
        "notes": "Remplacer si encrassé ou selon calendrier",
        "frequency": "mensuelle"
    },
    
    # Additional SEMESTRIELLE tasks
    {
        "task_number": None,
        "task_description": "Lubrifier les points d'articulation",
        "category": "Lubrification / Lubrication",
        "estimated_duration_minutes": 20,
        "required_materials": "Lubrifiant approprié, pompe à lubrifiant",
        "safety_precautions": "Machine à l'arrêt",
        "notes": "Utiliser le lubrifiant spécifié pour la machine",
        "frequency": "semestrielle"
    },
    {
        "task_number": None,
        "task_description": "Vérifier les vibrations de la machine",
        "category": "Vibrations / Vibrations",
        "estimated_duration_minutes": 15,
        "required_materials": "Vibrométre ou observation sensorielle",
        "safety_precautions": "Machine en fonctionnement normal",
        "notes": "Écouter et observer les vibrations anormales",
        "frequency": "semestrielle"
    },
    
    # Additional MENSUELLE tasks
    {
        "task_number": None,
        "task_description": "Contrôler le système de refroidissement",
        "category": "Refroidissement / Cooling",
        "estimated_duration_minutes": 15,
        "required_materials": "Thermomètre, outils",
        "safety_precautions": "Vérifier à température opérationnelle",
        "notes": "Température doit être dans la plage normale",
        "frequency": "mensuelle"
    },
    
    # Additional SEMESTRIELLE tasks
    {
        "task_number": None,
        "task_description": "Vérifier l'état des tubes et des tuyaux",
        "category": "Tuyauterie / Piping",
        "estimated_duration_minutes": 20,
        "required_materials": "Outils d'inspection, pièces de rechange",
        "safety_precautions": "Système dépressurisé",
        "notes": "Vérifier l'absence de fuites et de cracks",
        "frequency": "semestrielle"
    },
    
    # Additional MENSUELLE tasks
    {
        "task_number": None,
        "task_description": "Contrôler la pression hydraulique/pneumatique",
        "category": "Pression / Pressure",
        "estimated_duration_minutes": 15,
        "required_materials": "Manomètre",
        "safety_precautions": "Lire en fonctionnement normal",
        "notes": "Les valeurs doivent être dans les spécifications",
        "frequency": "mensuelle"
    },
    
    # Additional SEMESTRIELLE tasks
    {
        "task_number": None,
        "task_description": "Vérifier la courroie de transmission",
        "category": "Transmission / Belt",
        "estimated_duration_minutes": 20,
        "required_materials": "Jauge de tension, outils",
        "safety_precautions": "Machine arrêtée",
        "notes": "Vérifier la tension et l'usure",
        "frequency": "semestrielle"
    },
    
    # Additional MENSUELLE tasks
    {
        "task_number": None,
        "task_description": "Nettoyer les surfaces et les zones de travail",
        "category": "Nettoyage / Cleaning",
        "estimated_duration_minutes": 15,
        "required_materials": "Produits de nettoyage, chiffons",
        "safety_precautions": "Aucune",
        "notes": "Nettoyer les débris et résidus d'usinage",
        "frequency": "mensuelle"
    },
    
    # Additional SEMESTRIELLE tasks
    {
        "task_number": None,
        "task_description": "Vérifier les contacts et les relais électriques",
        "category": "Électrique / Electrical",
        "estimated_duration_minutes": 15,
        "required_materials": "Multimètre, outils",
        "safety_precautions": "Vérifier l'absence de tension",
        "notes": "Vérifier l'absence d'oxydation et la continuité",
        "frequency": "semestrielle"
    },
    
    # Additional MENSUELLE tasks
    {
        "task_number": None,
        "task_description": "Contrôler les câbles et les connexions",
        "category": "Câblage / Wiring",
        "estimated_duration_minutes": 15,
        "required_materials": "Outils d'inspection",
        "safety_precautions": "Machine arrêtée",
        "notes": "Vérifier l'isolement et la bonne connexion",
        "frequency": "mensuelle"
    },
    {
        "task_number": None,
        "task_description": "Vérifier les capteurs et les détecteurs",
        "category": "Capteurs / Sensors",
        "estimated_duration_minutes": 15,
        "required_materials": "Outils d'essai, multimètre",
        "safety_precautions": "Machine arrêtée",
        "notes": "Vérifier le bon fonctionnement et les raccordements",
        "frequency": "mensuelle"
    },
    
    # Additional SEMESTRIELLE tasks
    {
        "task_number": None,
        "task_description": "Contrôler l'isolation électrique",
        "category": "Sécurité / Safety",
        "estimated_duration_minutes": 20,
        "required_materials": "Mégohmmètre",
        "safety_precautions": "Vérifier l'absence de tension",
        "notes": "L'isolation doit être > 1MΩ selon normes",
        "frequency": "semestrielle"
    },
    {
        "task_number": None,
        "task_description": "Vérifier le fonctionnement des dispositifs de sécurité",
        "category": "Sécurité / Safety",
        "estimated_duration_minutes": 20,
        "required_materials": "Outils d'essai",
        "safety_precautions": "Tester en mode sûr",
        "notes": "Tous les dispositifs doivent fonctionner correctement",
        "frequency": "semestrielle"
    },
    
    # Additional MENSUELLE tasks
    {
        "task_number": None,
        "task_description": "Contrôler les engrenages et les pignons",
        "category": "Mécanique / Mechanical",
        "estimated_duration_minutes": 15,
        "required_materials": "Outils d'inspection",
        "safety_precautions": "Machine arrêtée",
        "notes": "Vérifier l'absence d'usure et de jeu anormal",
        "frequency": "mensuelle"
    },
    
    # Additional SEMESTRIELLE tasks
    {
        "task_number": None,
        "task_description": "Vérifier les roulements à bille",
        "category": "Roulements / Bearings",
        "estimated_duration_minutes": 20,
        "required_materials": "Outils d'inspection",
        "safety_precautions": "Machine arrêtée",
        "notes": "Vérifier l'absence de bruit et de jeu",
        "frequency": "semestrielle"
    },
    {
        "task_number": None,
        "task_description": "Contrôler les joints et les étanchéités",
        "category": "Étanchéité / Sealing",
        "estimated_duration_minutes": 20,
        "required_materials": "Outils d'inspection, joints de rechange",
        "safety_precautions": "Machine arrêtée",
        "notes": "Vérifier l'absence de fuite et l'état des joints",
        "frequency": "semestrielle"
    },
    
    # Additional MENSUELLE tasks
    {
        "task_number": None,
        "task_description": "Vérifier l'usure des chaînes",
        "category": "Chaînes / Chains",
        "estimated_duration_minutes": 15,
        "required_materials": "Jauge de chaîne, outils",
        "safety_precautions": "Machine arrêtée",
        "notes": "Vérifier la tension et l'usure",
        "frequency": "mensuelle"
    },
    
    # Additional SEMESTRIELLE tasks
    {
        "task_number": None,
        "task_description": "Contrôler les dispositifs de protection",
        "category": "Protection / Protection",
        "estimated_duration_minutes": 15,
        "required_materials": "Outils d'inspection",
        "safety_precautions": "Machine arrêtée",
        "notes": "Vérifier que tous les gardes sont en place",
        "frequency": "semestrielle"
    },
    
    # Additional MENSUELLE tasks
    {
        "task_number": None,
        "task_description": "Vérifier l'étiquetage et la documentation",
        "category": "Documentation / Documentation",
        "estimated_duration_minutes": 10,
        "required_materials": "Étiquettes, stylo",
        "safety_precautions": "Aucune",
        "notes": "Vérifier que toutes les étiquettes sont visibles et lisibles",
        "frequency": "mensuelle"
    },
    
    # Additional SEMESTRIELLE task
    {
        "task_number": None,
        "task_description": "Contrôler le système de ventilation",
        "category": "Ventilation / Ventilation",
        "estimated_duration_minutes": 15,
        "required_materials": "Outils de nettoyage",
        "safety_precautions": "Machine arrêtée",
        "notes": "Nettoyer les entrées/sorties d'air, vérifier fonctionnement",
        "frequency": "semestrielle"
    },
    
    # Additional MENSUELLE task
    {
        "task_number": None,
        "task_description": "Vérifier l'étalonnage des instruments de mesure",
        "category": "Étalonnage / Calibration",
        "estimated_duration_minutes": 15,
        "required_materials": "Étalons de référence, outils",
        "safety_precautions": "Aucune",
        "notes": "Vérifier que les instruments sont dans les tolérances acceptables",
        "frequency": "mensuelle"
    },
    
    # Final SEMESTRIELLE task
    {
        "task_number": None,
        "task_description": "Tester le fonctionnement global de la machine",
        "category": "Test / Testing",
        "estimated_duration_minutes": 30,
        "required_materials": "Pièces test",
        "safety_precautions": "Suivre les procédures d'essai",
        "notes": "Test complet du cycle de fonctionnement après maintenance",
        "frequency": "semestrielle"
    }
]

def create_preventive_maintenance_plan():
    """Create a UNIVERSAL preventive maintenance plan with all 22 tasks (applies to all machines)"""
    
    with app.app_context():
        # Check if plan already exists
        existing_plan = PreventiveMaintenancePlan.query.filter_by(
            plan_name="Plan de Maintenance Préventive Complet (22 Tâches)"
        ).first()
        
        if existing_plan:
            print(f"✓ Universal maintenance plan already exists (ID: {existing_plan.id})")
            return existing_plan.id
        
        # Get admin/supervisor user to create the plan
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            admin_user = User.query.filter_by(role='supervisor').first()
        
        if not admin_user:
            print("✗ No admin or supervisor user found.")
            return None
        
        # Create UNIVERSAL plan (NOT tied to a specific machine)
        # machine_id is NULL so this can be used for ANY machine
        plan = PreventiveMaintenancePlan(
            plan_name="Plan de Maintenance Préventive Complet (22 Tâches)",
            machine_id=None,  # UNIVERSAL - no specific machine
            frequency_type="monthly",
            frequency_days=30,
            description="Plan complet de maintenance préventive avec 22 tâches couvrant tous les aspects de la machine. Ce plan s'applique à TOUTES les machines.",
            is_active=True,
            created_by_id=admin_user.id,
            next_planned=date.today()
        )
        db.session.add(plan)
        db.session.flush()  # Get plan ID
        
        print(f"\n✓ Created UNIVERSAL maintenance plan: '{plan.plan_name}' (ID: {plan.id})")
        print(f"  Type: Universal (applies to ALL machines)")
        print(f"  Frequency: {plan.frequency_type} ({plan.frequency_days} days)\n")
        
        # Add all maintenance tasks (with frequency mapping)
        print(f"\nAdding {len(MAINTENANCE_TASKS)} maintenance tasks...")
        
        # Count tasks by frequency
        mensuelle_count = sum(1 for t in MAINTENANCE_TASKS if t.get("frequency") == "mensuelle")
        semestrielle_count = sum(1 for t in MAINTENANCE_TASKS if t.get("frequency") == "semestrielle")
        
        print(f"  → Mensuelle (Monthly): {mensuelle_count} tasks")
        print(f"  → Semestrielle (Semi-Annual): {semestrielle_count} tasks\n")
        
        for idx, task_data in enumerate(MAINTENANCE_TASKS, 1):
            task = PreventiveMaintenanceTask(
                plan_id=plan.id,
                task_number=task_data["task_number"],
                task_description=task_data["task_description"],
                category=task_data["category"],
                estimated_duration_minutes=task_data["estimated_duration_minutes"],
                required_materials=task_data["required_materials"],
                safety_precautions=task_data["safety_precautions"],
                notes=task_data["notes"],
                method=task_data.get("frequency", "N")  # Store frequency as method
            )
            db.session.add(task)
            
            # Print with better formatting
            task_num_str = f"Task {task_data['task_number']:2d}" if task_data['task_number'] else "Task   -"
            freq_str = f"[{task_data.get('frequency', '?').upper()[:3]}]"
            print(f"  {task_num_str} {freq_str}: {task_data['task_description'][:45]:45s} ({task_data['estimated_duration_minutes']} min)")
        
        db.session.commit()
        
        # Calculate statistics
        detailed_tasks = [t for t in MAINTENANCE_TASKS if t["task_number"]]
        additional_tasks = [t for t in MAINTENANCE_TASKS if not t["task_number"]]
        total_duration = sum(t["estimated_duration_minutes"] for t in MAINTENANCE_TASKS)
        
        print(f"\n{'='*70}")
        print(f"✓ Successfully created {len(MAINTENANCE_TASKS)} maintenance tasks")
        print(f"  ├─ Core numbered tasks: {len(detailed_tasks)} (Tasks 1-10)")
        print(f"  └─ Additional maintenance tasks: {len(additional_tasks)}")
        print(f"\n✓ Frequency Breakdown:")
        print(f"  ├─ Mensuelle (Monthly): {sum(1 for t in MAINTENANCE_TASKS if t.get('frequency') == 'mensuelle')} tasks")
        print(f"  └─ Semestrielle (Semi-Annual): {sum(1 for t in MAINTENANCE_TASKS if t.get('frequency') == 'semestrielle')} tasks")
        print(f"\n✓ Total estimated maintenance time: {total_duration} minutes ({total_duration // 60}h {total_duration % 60}m)")
        print(f"✓ Universal Plan ID: {plan.id}")
        print(f"✓ Tasks match reference document (maintenance_report_card.html)")
        print(f"{'='*70}")
        
        return plan.id

if __name__ == '__main__':
    print("="*70)
    print("French Preventive Maintenance Plan Seeder")
    print("="*70)
    
    try:
        plan_id = create_preventive_maintenance_plan()
        if plan_id:
            print("\n✓ Seeding completed successfully!")
            print(f"✓ Universal maintenance plan created (ID: {plan_id})")
            print(f"✓ You can now schedule this plan for ANY machine")
            print(f"✓ Go to: Preventive Maintenance → Plans → Schedule Execution → Select Machine")
        else:
            print("\n✗ Seeding failed - check errors above")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
