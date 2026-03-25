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
-- Table structure for table `preventive_maintenance_task_executions`
--

DROP TABLE IF EXISTS `preventive_maintenance_task_executions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `preventive_maintenance_task_executions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `execution_id` int NOT NULL,
  `task_id` int NOT NULL,
  `technician_id` int DEFAULT NULL,
  `order_number` int DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `actual_duration_minutes` int DEFAULT NULL,
  `findings` text,
  `actions_taken` text,
  `issues_encountered` text,
  `materials_used` text,
  `completion_notes` text,
  `quality_check` varchar(50) DEFAULT NULL,
  `quality_notes` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `task_id` (`task_id`),
  KEY `technician_id` (`technician_id`),
  KEY `ix_preventive_maintenance_task_executions_execution_id` (`execution_id`),
  CONSTRAINT `preventive_maintenance_task_executions_ibfk_1` FOREIGN KEY (`execution_id`) REFERENCES `preventive_maintenance_executions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `preventive_maintenance_task_executions_ibfk_2` FOREIGN KEY (`task_id`) REFERENCES `preventive_maintenance_tasks` (`id`),
  CONSTRAINT `preventive_maintenance_task_executions_ibfk_3` FOREIGN KEY (`technician_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `preventive_maintenance_task_executions`
--

LOCK TABLES `preventive_maintenance_task_executions` WRITE;
/*!40000 ALTER TABLE `preventive_maintenance_task_executions` DISABLE KEYS */;
INSERT INTO `preventive_maintenance_task_executions` VALUES (1,1,1,NULL,1,'pending',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'passed',NULL,'2026-03-10 11:22:50','2026-03-10 11:22:50'),(2,1,2,NULL,2,'pending',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'passed',NULL,'2026-03-10 11:22:50','2026-03-10 11:22:50'),(3,1,3,NULL,3,'pending',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'passed',NULL,'2026-03-10 11:22:50','2026-03-10 11:22:50'),(4,1,4,NULL,4,'pending',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'passed',NULL,'2026-03-10 11:22:50','2026-03-10 11:22:50');
/*!40000 ALTER TABLE `preventive_maintenance_task_executions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-17 12:13:56
