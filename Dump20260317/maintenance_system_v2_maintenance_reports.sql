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
-- Table structure for table `maintenance_reports`
--

DROP TABLE IF EXISTS `maintenance_reports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `maintenance_reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `schedule_id` int DEFAULT NULL,
  `technician_id` int NOT NULL,
  `machine_name` varchar(200) DEFAULT NULL,
  `actual_start_time` datetime DEFAULT NULL,
  `actual_end_time` datetime DEFAULT NULL,
  `actual_duration_hours` float DEFAULT NULL,
  `work_description` text,
  `findings` text,
  `actions_taken` text,
  `issues_found` tinyint(1) DEFAULT '0',
  `issue_description` text,
  `components_replaced` text,
  `next_maintenance_recommendation` text,
  `report_type` varchar(50) DEFAULT 'standard',
  `report_status` varchar(50) DEFAULT 'draft',
  `technician_zone` varchar(100) DEFAULT NULL,
  `machine_condition` varchar(50) DEFAULT NULL,
  `machine_condition_after` varchar(50) DEFAULT NULL,
  `environmental_conditions` text,
  `safety_observations` text,
  `tools_used` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `supervisor_id` int DEFAULT NULL,
  `supervisor_approval_status` varchar(50) DEFAULT 'pending',
  `supervisor_approval_date` datetime DEFAULT NULL,
  `supervisor_notes` text,
  `checklist_data` longtext,
  PRIMARY KEY (`id`),
  KEY `schedule_id` (`schedule_id`),
  KEY `idx_technician_id` (`technician_id`),
  KEY `idx_status` (`report_status`),
  KEY `supervisor_id` (`supervisor_id`),
  KEY `idx_supervisor_approval_status` (`supervisor_approval_status`),
  CONSTRAINT `maintenance_reports_ibfk_1` FOREIGN KEY (`schedule_id`) REFERENCES `maintenance_schedules` (`id`) ON DELETE CASCADE,
  CONSTRAINT `maintenance_reports_ibfk_2` FOREIGN KEY (`technician_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `maintenance_reports_ibfk_3` FOREIGN KEY (`supervisor_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maintenance_reports`
--

LOCK TABLES `maintenance_reports` WRITE;
/*!40000 ALTER TABLE `maintenance_reports` DISABLE KEYS */;
INSERT INTO `maintenance_reports` VALUES (1,3,3,'Winding Machine','2026-03-02 08:00:00','2026-03-02 09:00:00',1,'changed water pump ','nothing','replaced ',0,'','water pump','i dont know ','standard','approved',NULL,NULL,NULL,NULL,NULL,NULL,'2026-03-02 07:37:04','2026-03-02 07:45:57',NULL,'pending',NULL,NULL,NULL),(2,1,5,'Assembly Line 1','2026-03-02 07:13:00','2026-03-02 13:13:00',6,'best work ever ','nothing ','go home ',0,'','i dont know','i dont know ','comprehensive','approved','Zone A','good','good',NULL,'need the phse team ',NULL,'2026-03-02 08:15:05','2026-03-02 08:16:18',NULL,'pending',NULL,NULL,NULL),(3,1,5,'Assembly Line 1','2026-03-01 08:14:00','2026-03-01 09:17:00',1.05,'test','test','test',1,'test','test','test','comprehensive','submitted','Zone A','excellent','excellent',NULL,'test',NULL,'2026-03-02 08:18:02','2026-03-02 08:18:02',NULL,'pending',NULL,NULL,NULL),(4,NULL,3,'Assembly Line 1',NULL,'2026-03-17 09:17:03',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 08:17:03','2026-03-17 08:17:03',NULL,'pending',NULL,NULL,NULL),(5,NULL,3,'Assembly Line 1',NULL,'2026-03-17 09:17:23',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 08:17:23','2026-03-17 08:17:23',NULL,'pending',NULL,NULL,NULL),(6,NULL,3,'Assembly Line 1',NULL,'2026-03-17 09:20:33',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 08:20:33','2026-03-17 08:20:33',NULL,'pending',NULL,NULL,NULL),(7,NULL,3,'Assembly Line 1',NULL,'2026-03-17 09:53:25',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 08:53:25','2026-03-17 08:53:25',NULL,'pending',NULL,NULL,NULL),(8,NULL,3,'Assembly Line 1',NULL,'2026-03-17 09:58:44',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 08:58:44','2026-03-17 08:58:44',NULL,'pending',NULL,NULL,NULL),(9,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:01:01',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:01:01','2026-03-17 09:01:01',NULL,'pending',NULL,NULL,NULL),(10,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:02:15',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:02:15','2026-03-17 09:02:15',NULL,'pending',NULL,NULL,NULL),(11,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:03:25',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:03:25','2026-03-17 09:03:25',NULL,'pending',NULL,NULL,NULL),(12,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:18:38',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:18:38','2026-03-17 09:18:38',NULL,'pending',NULL,NULL,NULL),(13,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:19:36',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:19:36','2026-03-17 09:19:36',NULL,'pending',NULL,NULL,NULL),(14,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:25:12',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:25:12','2026-03-17 09:25:12',NULL,'pending',NULL,NULL,NULL),(15,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:27:30',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:27:30','2026-03-17 09:27:30',NULL,'pending',NULL,NULL,NULL),(16,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:27:55',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:27:55','2026-03-17 09:27:55',NULL,'pending',NULL,NULL,NULL),(17,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:29:03',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:29:03','2026-03-17 09:29:03',NULL,'pending',NULL,NULL,NULL),(18,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:32:09',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:32:09','2026-03-17 09:32:09',NULL,'pending',NULL,NULL,NULL),(19,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:33:42',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:33:42','2026-03-17 09:33:42',NULL,'pending',NULL,NULL,NULL),(20,NULL,3,'Assembly Line 1',NULL,'2026-03-17 10:49:16',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 09:49:16','2026-03-17 09:49:16',NULL,'pending',NULL,NULL,NULL),(21,NULL,3,'Assembly Line 1',NULL,'2026-03-17 11:01:09',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 10:01:09','2026-03-17 10:01:09',NULL,'pending',NULL,NULL,NULL),(22,NULL,3,'Testing Station',NULL,'2026-03-17 11:02:20',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 10:02:20','2026-03-17 10:02:20',NULL,'pending',NULL,NULL,NULL),(23,NULL,3,'Testing Station',NULL,'2026-03-17 11:11:53',NULL,'test',NULL,NULL,0,NULL,NULL,NULL,'standard','submitted','test',NULL,NULL,'test','',NULL,'2026-03-17 10:11:53','2026-03-17 10:11:53',NULL,'pending',NULL,NULL,NULL);
/*!40000 ALTER TABLE `maintenance_reports` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-17 12:13:59
