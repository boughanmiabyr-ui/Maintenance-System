-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: maintenance_system_v2
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `preventive_maintenance_tasks`
--

DROP TABLE IF EXISTS `preventive_maintenance_tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preventive_maintenance_tasks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plan_id` int NOT NULL,
  `task_number` int DEFAULT NULL,
  `task_description` text NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `estimated_duration_minutes` int DEFAULT NULL,
  `required_materials` text,
  `safety_precautions` text,
  `notes` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `method` varchar(10) DEFAULT 'N',
  PRIMARY KEY (`id`),
  KEY `ix_preventive_maintenance_tasks_plan_id` (`plan_id`),
  CONSTRAINT `preventive_maintenance_tasks_ibfk_1` FOREIGN KEY (`plan_id`) REFERENCES `preventive_maintenance_plans` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preventive_maintenance_tasks`
--

LOCK TABLES `preventive_maintenance_tasks` WRITE;
/*!40000 ALTER TABLE `preventive_maintenance_tasks` DISABLE KEYS */;
INSERT INTO `preventive_maintenance_tasks` VALUES (1,2,1,'Check electrical connections',NULL,30,NULL,NULL,NULL,'2026-03-10 11:22:50','2026-03-10 11:22:50','N'),(2,2,2,'Lubricate moving parts',NULL,45,NULL,NULL,NULL,'2026-03-10 11:22:50','2026-03-10 11:22:50','N'),(3,2,3,'Inspect safety systems',NULL,20,NULL,NULL,NULL,'2026-03-10 11:22:50','2026-03-10 11:22:50','N'),(4,2,4,'Clean work area',NULL,15,NULL,NULL,NULL,'2026-03-10 11:22:50','2026-03-10 11:22:50','N'),(27,7,1,'Vérifier le système de sécurité de la machine (Arrêt d\'urgence, marche-Arrêt…)','Safety',15,'Aucun','Arrêter complètement la machine avant d\'effectuer cette vérification','Vérifier que chaque arrêt d\'urgence est capable d\'arrêter la machine. Chaque arrêt fonctionnel.','2026-03-12 09:51:50','2026-03-12 09:51:50','I'),(28,7,2,'Vérifier l\'état des accessoires liés au poste de travail (loupe, mètre, support d\'éclairage…)','Accessories',10,'Accessoires de vérification','Utiliser les équipements de protection appropriés','Les accessoires doivent exister et être en bon état','2026-03-12 09:51:50','2026-03-12 09:51:50','N'),(29,7,3,'Faire une purge pour évacuer l\'eau accumulée dans le conditionneur','Hydraulic',20,'Bac de récupération, outils','Placer le bac avant d\'ouvrir la purge','Ouvrir la purge pendant 1 minute. Voir fig 001','2026-03-12 09:51:50','2026-03-12 09:51:50','I'),(30,7,4,'Contrôler l\'œil enduit pour câble','Electrical',10,'Aucun','Vérifier l\'isolation des câbles','Pas d\'usure. Inspection visuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','N'),(31,7,5,'Vérifier la mobilité des roulements des redressement','Mechanical',15,'Aucun','Écouter attentivement le fonctionnement','Aucun bruit lors du fonctionnement. Inspection sensorielle','2026-03-12 09:51:50','2026-03-12 09:51:50','O'),(32,7,6,'Vérifier l\'usure des courroies, roues dentées et roulement','Mechanical',20,'Outils d\'inspection','Arrêter la machine avant l\'inspection','Pas d\'usures, pas de bavures. Voir fig 002. Inspection manuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','I'),(33,7,7,'Vérifier et nettoyer la roue d\'encoudeur avec une brosse en cuivre','Mechanical',25,'Brosse en cuivre, chiffon','Utiliser une brosse adaptée pour ne pas endommager','Aucune usure et aucune bavure sur la roue d\'encoudeur. Voir fig 003. Inspection manuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','I'),(34,7,8,'Vérifier la mobilité des pinces (grippers)','Mechanical',15,'Aucun','Vérifier en mode manuel seulement','Lors d\'activation de l\'option Basculer, les sorties aucune coincement de pinces. Inspection visuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','N'),(35,7,9,'Vérifier l\'état des couteaux','Mechanical',20,'Jauge de mesure','Faire attention aux arêtes tranchantes','Pas d\'usure. Voir fig 004. Produire 3 échantillons. Inspection visuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','N'),(36,7,10,'Vérifier la tension du courroie transporteuse','Mechanical',20,'Jauge de 0,35mm','Arrêter la machine avant d\'ajuster','Jeux entre tapis et reglette = 0,35mm. Voir fig 005. Inspection manuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','I'),(37,7,11,'Vérifier le bon fonctionnement du ventilateur du coffret électrique','Electrical',10,'Aucun','Vérifier en conditions d\'utilisation normales','Aucun coincement. Inspection visuelle et sensorielle','2026-03-12 09:51:50','2026-03-12 09:51:50','O'),(38,7,12,'Positionner à zéro les deux bras de pivottement','Mechanical',25,'Outils de calibrage','Utiliser les outils de calibrage appropriés','Les deux bras doivent être alignés avec le bloc de lame. Utiliser outils de calibrage fig 006','2026-03-12 09:51:50','2026-03-12 09:51:50','I'),(39,7,13,'Vérifier les manomètres de pression','Hydraulic',15,'Manomètre de référence','Lire les valeurs en conditions stables','Principal: 6-8 bar, Entraînement: 1,5-2,5 bar, Presse: 4-8 bar. Inspection visuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','N'),(40,7,14,'Vérification de l\'étalonnage des presses','Mechanical',30,'Outils d\'étalonnage ref. fig 007','Suivre la procédure d\'étalonnage','Cycle de presse correspond à un tour complet outil d\'étalonnage. Utiliser outils d\'étalonnage ref: fig 007','2026-03-12 09:51:50','2026-03-12 09:51:50','I'),(41,7,15,'Vérification les paramètres TOP WIN (CFA, tolérance de fil, longueur de dénudage...)','Electrical',20,'Accès à TOP WIN','Ne pas modifier les paramètres critiques','Les options de modification produit dans la session opérateur doivent être désactivées. Inspection visuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','N'),(42,7,16,'Vérifiez que l\'air comprimé sec seulement est utilisé','Pneumatic',15,'Hygromètre d\'air','Vérifier l\'installation du sécheur d\'air','Seulement l\'air sec est utilisé. Inspection manuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','I'),(43,7,17,'Vérifiez le mouvement d\'unité de redressement','Mechanical',15,'Aucun','Vérifier en mode manuel','Mouvement facile d\'unité. Inspection manuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','I'),(44,7,18,'Vérifier le réglage correct de l\'unité de dressage','Mechanical',20,'Outils de mesure','Arrêter la machine avant le réglage','La distance entre doigt doit être supérieure à la sortie. Voir fig 008','2026-03-12 09:51:50','2026-03-12 09:51:50','N'),(45,7,19,'Vérifier la déplacement des bras','Mechanical',15,'Aucun','Vérifier en mode manuel','Déplacement facile. Inspection visuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','N'),(46,7,20,'Vérifier les griffes de serrage de base outil usées ou non serrées','Mechanical',20,'Outils d\'inspection','Vérifier une fois l\'outil entièrement fixé','L\'outil est strictement fixé après montage. Inspection visuelle','2026-03-12 09:51:50','2026-03-12 09:51:50','N'),(47,7,21,'Vérification de la longueur','Quality',25,'Mètre de précision, 5 pièces test de 2000mm','Utiliser des instruments de précision','Aucune variation de longueur pour les échantillons produits. Tous les pièces doivent être dans l\'intervalle de tolérance. Pour 2000mm: tolérance (+-) 4mm suite PPE-MM-TN-024. Mesurer 5 pièces.','2026-03-12 09:51:50','2026-03-12 09:51:50','N'),(48,7,22,'Documentation et signature du rapport de maintenance','Administrative',15,'Rapport','Aucune','Documenter tous les travaux effectués, les observations et les problèmes rencontrés. Le technician doit signer le rapport.','2026-03-12 09:51:50','2026-03-12 09:51:50','N');
/*!40000 ALTER TABLE `preventive_maintenance_tasks` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-17 12:14:00
