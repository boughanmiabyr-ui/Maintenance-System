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
-- Table structure for table `preventive_maintenance_executions`
--

DROP TABLE IF EXISTS `preventive_maintenance_executions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preventive_maintenance_executions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `plan_id` int NOT NULL,
  `machine_id` int NOT NULL,
  `assigned_supervisor_id` int DEFAULT NULL,
  `assigned_technician_id` int DEFAULT NULL,
  `scheduled_date` date NOT NULL,
  `execution_date` date DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `report_status` varchar(50) DEFAULT NULL,
  `overall_findings` text,
  `machine_condition` varchar(50) DEFAULT NULL,
  `issues_found` tinyint(1) DEFAULT NULL,
  `issues_description` text,
  `recommendations` text,
  `spare_parts_needed` tinyint(1) DEFAULT NULL,
  `supervisor_approval_date` datetime DEFAULT NULL,
  `supervisor_notes` text,
  `supervision_status` varchar(50) DEFAULT NULL,
  `actual_start_time` datetime DEFAULT NULL,
  `actual_end_time` datetime DEFAULT NULL,
  `total_duration_minutes` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `machine_id` (`machine_id`),
  KEY `assigned_supervisor_id` (`assigned_supervisor_id`),
  KEY `assigned_technician_id` (`assigned_technician_id`),
  KEY `ix_preventive_maintenance_executions_scheduled_date` (`scheduled_date`),
  KEY `ix_preventive_maintenance_executions_plan_id` (`plan_id`),
  KEY `ix_preventive_maintenance_executions_status` (`status`),
  KEY `ix_preventive_maintenance_executions_execution_date` (`execution_date`),
  CONSTRAINT `preventive_maintenance_executions_ibfk_1` FOREIGN KEY (`plan_id`) REFERENCES `preventive_maintenance_plans` (`id`) ON DELETE CASCADE,
  CONSTRAINT `preventive_maintenance_executions_ibfk_2` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`),
  CONSTRAINT `preventive_maintenance_executions_ibfk_3` FOREIGN KEY (`assigned_supervisor_id`) REFERENCES `users` (`id`),
  CONSTRAINT `preventive_maintenance_executions_ibfk_4` FOREIGN KEY (`assigned_technician_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preventive_maintenance_executions`
--

LOCK TABLES `preventive_maintenance_executions` WRITE;
/*!40000 ALTER TABLE `preventive_maintenance_executions` DISABLE KEYS */;
INSERT INTO `preventive_maintenance_executions` VALUES (1,2,1,2,3,'2026-03-15',NULL,'scheduled','draft',NULL,NULL,0,NULL,NULL,0,NULL,NULL,'pending',NULL,NULL,NULL,'2026-03-10 11:22:50','2026-03-10 11:22:50');
/*!40000 ALTER TABLE `preventive_maintenance_executions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-17 12:13:57
