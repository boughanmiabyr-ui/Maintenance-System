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
-- Table structure for table `preventive_maintenance_plans`
--

DROP TABLE IF EXISTS `preventive_maintenance_plans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preventive_maintenance_plans` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plan_name` varchar(150) NOT NULL,
  `machine_id` int DEFAULT NULL,
  `frequency_type` varchar(50) DEFAULT NULL,
  `frequency_days` int DEFAULT NULL,
  `description` text,
  `last_execution` datetime DEFAULT NULL,
  `next_planned` date DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_by_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by_id` (`created_by_id`),
  KEY `ix_preventive_maintenance_plans_is_active` (`is_active`),
  KEY `ix_preventive_maintenance_plans_machine_id` (`machine_id`),
  CONSTRAINT `preventive_maintenance_plans_ibfk_1` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`) ON DELETE CASCADE,
  CONSTRAINT `preventive_maintenance_plans_ibfk_2` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preventive_maintenance_plans`
--

LOCK TABLES `preventive_maintenance_plans` WRITE;
/*!40000 ALTER TABLE `preventive_maintenance_plans` DISABLE KEYS */;
INSERT INTO `preventive_maintenance_plans` VALUES (2,'Monthly Assembly Line Maintenance',1,'monthly',30,'Regular maintenance for Assembly Line 1',NULL,'2026-03-10',1,2,'2026-03-10 11:22:50','2026-03-10 11:22:50'),(3,'test',1,'monthly',30,'',NULL,'2026-03-10',1,2,'2026-03-10 12:24:55','2026-03-10 12:24:55'),(7,'Plan de Maintenance Préventive Complet (22 Tâches)',NULL,'monthly',30,'Plan complet de maintenance préventive avec 22 tâches couvrant tous les aspects de la machine. Ce plan s\'applique à TOUTES les machines.',NULL,'2026-03-12',1,1,'2026-03-12 09:51:50','2026-03-12 09:51:50');
/*!40000 ALTER TABLE `preventive_maintenance_plans` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-17 12:13:55
