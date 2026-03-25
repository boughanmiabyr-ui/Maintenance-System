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
-- Table structure for table `machine_events`
--

DROP TABLE IF EXISTS `machine_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `machine_events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `machine_id` int NOT NULL,
  `machine_name` varchar(200) DEFAULT NULL,
  `event_type` varchar(50) NOT NULL,
  `event_status` varchar(50) DEFAULT NULL,
  `start_user_id` varchar(100) DEFAULT NULL,
  `end_user_id` varchar(100) DEFAULT NULL,
  `start_comment` text,
  `end_comment` text,
  `cancel_reason` text,
  `breakdown_type` varchar(100) DEFAULT NULL,
  `event_start_time` datetime NOT NULL,
  `event_end_time` datetime DEFAULT NULL,
  `duration_seconds` float DEFAULT NULL,
  `reaction_time_seconds` float DEFAULT NULL,
  `maintenance_arrival_time` datetime DEFAULT NULL,
  `maintenance_arrival_user_id` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_machine_events_machine_id` (`machine_id`),
  KEY `ix_machine_events_created_at` (`created_at`),
  CONSTRAINT `machine_events_ibfk_1` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `machine_events`
--

LOCK TABLES `machine_events` WRITE;
/*!40000 ALTER TABLE `machine_events` DISABLE KEYS */;
INSERT INTO `machine_events` VALUES (1,1,'MACH001','maintenance','started','1414',NULL,'Maintenance',NULL,NULL,'Maintenance','2026-03-16 11:37:47',NULL,NULL,17.3579,'2026-03-16 12:07:57','5574','2026-03-16 11:37:47','2026-03-16 12:07:57'),(2,1,'MACH001','break','ended','1111','1111','arij','arij',NULL,NULL,'2026-03-16 11:57:41','2026-03-16 11:58:04',23.37,NULL,NULL,NULL,'2026-03-16 11:57:41','2026-03-16 11:58:04'),(3,1,'MACH001','maintenance','started','444',NULL,'Maintenance',NULL,NULL,'Maintenance','2026-03-16 12:09:31',NULL,NULL,23.6554,'2026-03-16 12:09:42','525','2026-03-16 12:09:31','2026-03-16 12:09:42'),(4,1,'MACH001','downtime','ended','111','9696','','ariiiiij',NULL,NULL,'2026-03-16 12:10:54','2026-03-16 12:11:15',21.1117,NULL,NULL,NULL,'2026-03-16 12:10:54','2026-03-16 12:11:15');
/*!40000 ALTER TABLE `machine_events` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-17 12:13:58
