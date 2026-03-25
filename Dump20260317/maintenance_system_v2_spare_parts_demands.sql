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
-- Table structure for table `spare_parts_demands`
--

DROP TABLE IF EXISTS `spare_parts_demands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `spare_parts_demands` (
  `id` int NOT NULL AUTO_INCREMENT,
  `demand_number` varchar(50) NOT NULL,
  `maintenance_report_id` int DEFAULT NULL,
  `requestor_id` int NOT NULL,
  `department_id` int DEFAULT NULL,
  `material_id` int NOT NULL,
  `quantity_requested` int NOT NULL,
  `priority` enum('low','medium','high','urgent') DEFAULT 'medium',
  `reason` text,
  `supervisor_id` int DEFAULT NULL,
  `supervisor_approval` enum('pending','approved','rejected') DEFAULT 'pending',
  `supervisor_approval_date` datetime DEFAULT NULL,
  `supervisor_notes` text,
  `stock_agent_id` int DEFAULT NULL,
  `stock_agent_approval` enum('pending','approved','rejected','partial') DEFAULT 'pending',
  `stock_agent_approval_date` datetime DEFAULT NULL,
  `quantity_allocated` int DEFAULT NULL,
  `stock_agent_notes` text,
  `quantity_returned` int DEFAULT '0',
  `return_date` datetime DEFAULT NULL,
  `return_notes` text,
  `demand_status` enum('pending','supervisor_review','approved_supervisor','stock_agent_review','approved_stock_agent','rejected','partial_allocated','fulfilled','cancelled','archived') DEFAULT 'pending',
  `fulfilled_date` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `archive_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `demand_number` (`demand_number`),
  KEY `maintenance_report_id` (`maintenance_report_id`),
  KEY `idx_created_at` (`created_at`),
  KEY `idx_demands_status` (`demand_status`),
  KEY `idx_material_id` (`material_id`),
  KEY `requestor_id` (`requestor_id`),
  KEY `supervisor_id` (`supervisor_id`),
  KEY `stock_agent_id` (`stock_agent_id`),
  KEY `idx_department_demands` (`department_id`),
  KEY `idx_archive_date` (`archive_date`),
  KEY `idx_status_archived` (`demand_status`,`archive_date`),
  CONSTRAINT `spare_parts_demands_ibfk_1` FOREIGN KEY (`maintenance_report_id`) REFERENCES `maintenance_reports` (`id`) ON DELETE SET NULL,
  CONSTRAINT `spare_parts_demands_ibfk_2` FOREIGN KEY (`requestor_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `spare_parts_demands_ibfk_3` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`) ON DELETE CASCADE,
  CONSTRAINT `spare_parts_demands_ibfk_4` FOREIGN KEY (`supervisor_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `spare_parts_demands_ibfk_5` FOREIGN KEY (`stock_agent_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `spare_parts_demands`
--

LOCK TABLES `spare_parts_demands` WRITE;
/*!40000 ALTER TABLE `spare_parts_demands` DISABLE KEYS */;
INSERT INTO `spare_parts_demands` VALUES (1,'DEM-20260302-63C11B',1,5,NULL,115,1,'medium','needed nowwwwww',2,'approved','2026-03-02 10:18:02','nothing ',4,'approved','2026-03-02 10:44:04',1,'',0,NULL,NULL,'approved_stock_agent','2026-03-02 10:44:04','2026-03-02 09:06:59','2026-03-02 09:44:04',NULL),(2,'DEM-20260303-8C3B80',1,5,NULL,3,1,'urgent','i need it for x machine',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 10:31:02','2026-03-03 10:31:02',NULL),(3,'DEM-20260303-A7688F',1,5,NULL,17,10,'urgent','i need it for x machine',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 10:31:02','2026-03-03 10:31:02',NULL),(4,'DEM-20260303-FE8193',1,5,NULL,27,2,'urgent','i need it for x machine',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 10:31:02','2026-03-03 10:31:02',NULL),(5,'DEM-20260303-0940A9',1,2,NULL,36,10,'high','test',NULL,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'pending',NULL,'2026-03-03 10:37:29','2026-03-03 10:37:29',NULL),(6,'DEM-20260303-7EB5ED',1,2,NULL,48,2,'high','test',NULL,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'pending',NULL,'2026-03-03 10:37:29','2026-03-03 10:37:29',NULL),(7,'DEM-20260303-F01CDC',1,2,NULL,87,1,'high','test',NULL,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'pending',NULL,'2026-03-03 10:37:29','2026-03-03 10:37:29',NULL),(8,'DEM-20260303-9CB198',1,2,NULL,92,1,'high','test',NULL,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'pending',NULL,'2026-03-03 10:37:29','2026-03-03 10:37:29',NULL),(11,'DEM-20260303-AEA352-A',2,5,NULL,10,1,'high','test',2,'approved','2026-03-03 11:47:26','',4,'approved','2026-03-03 11:49:09',1,'',0,NULL,NULL,'approved_stock_agent','2026-03-03 11:49:09','2026-03-03 10:46:20','2026-03-03 10:49:09',NULL),(12,'DEM-20260303-AEA352-B',2,5,NULL,21,1,'high','test',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 10:46:20','2026-03-03 10:46:20',NULL),(13,'DEM-20260303-AEA352-C',2,5,NULL,55,1,'high','test',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 10:46:20','2026-03-03 10:46:20',NULL),(14,'DEM-20260303-59A4DB-A',1,3,NULL,14,1,'medium','test',NULL,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'pending',NULL,'2026-03-03 10:50:43','2026-03-03 10:50:43',NULL),(15,'DEM-20260303-59A4DB-B',1,3,NULL,18,20,'medium','test',NULL,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'pending',NULL,'2026-03-03 10:50:43','2026-03-03 10:50:43',NULL),(16,'DEM-20260303-59A4DB-C',1,3,NULL,48,10,'medium','test',NULL,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'pending',NULL,'2026-03-03 10:50:43','2026-03-03 10:50:43',NULL),(17,'DEM-20260303-59A4DB-D',1,3,NULL,101,1,'medium','test',NULL,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'pending',NULL,'2026-03-03 10:50:43','2026-03-03 10:50:43',NULL),(18,'DEM-20260303-7ED4ED-A',1,3,NULL,18,1,'high','hgfghfghfghfhgfgd',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 10:51:46','2026-03-03 10:51:46',NULL),(19,'DEM-20260303-7ED4ED-B',1,3,NULL,42,5,'high','hgfghfghfghfhgfgd',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 10:51:46','2026-03-03 10:51:46',NULL),(20,'DEM-20260303-7ED4ED-C',1,3,NULL,109,10,'high','hgfghfghfghfhgfgd',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 10:51:46','2026-03-03 10:51:46',NULL),(21,'DEM-20260303-A1192F-A',1,3,NULL,16,19,'high','test',2,'approved','2026-03-03 12:00:55','',4,'partial','2026-03-03 12:02:06',1,'',0,NULL,NULL,'partial_allocated','2026-03-03 12:02:06','2026-03-03 10:59:56','2026-03-03 11:02:06',NULL),(22,'DEM-20260303-A1192F-B',1,3,NULL,102,10,'high','test',2,'approved','2026-03-03 12:00:55','',4,'partial','2026-03-03 12:02:06',1,'',0,NULL,NULL,'partial_allocated','2026-03-03 12:02:06','2026-03-03 10:59:56','2026-03-03 11:02:06',NULL),(23,'DEM-20260303-A1192F-C',1,3,NULL,134,1,'high','test',2,'approved','2026-03-03 12:00:55','',4,'approved','2026-03-03 12:02:06',1,'',0,NULL,NULL,'approved_stock_agent','2026-03-03 12:02:06','2026-03-03 10:59:56','2026-03-03 11:02:06',NULL),(24,'DEM-20260303-0BEE05-A',1,3,NULL,16,4,'urgent','hukybytf',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 15:01:18','2026-03-03 15:01:18',NULL),(25,'DEM-20260303-0BEE05-B',1,3,NULL,5,1,'urgent','hukybytf',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 15:01:18','2026-03-03 15:01:18',NULL),(26,'DEM-20260303-0BEE05-C',1,3,NULL,21,6,'urgent','hukybytf',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 15:01:18','2026-03-03 15:01:18',NULL),(27,'DEM-20260303-FB4CA4-A',1,3,NULL,16,4,'urgent','hukybytf',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 15:01:20','2026-03-03 15:01:20',NULL),(28,'DEM-20260303-FB4CA4-B',1,3,NULL,5,1,'urgent','hukybytf',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 15:01:20','2026-03-03 15:01:20',NULL),(29,'DEM-20260303-FB4CA4-C',1,3,NULL,21,6,'urgent','hukybytf',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-03 15:01:20','2026-03-03 15:01:20',NULL),(30,'DEM-20260303-4D303B-A',1,3,NULL,16,4,'urgent','hukybytf',2,'approved','2026-03-03 16:02:18','',NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'approved_supervisor',NULL,'2026-03-03 15:01:24','2026-03-03 15:02:18',NULL),(31,'DEM-20260303-4D303B-B',1,3,NULL,5,1,'urgent','hukybytf',2,'approved','2026-03-03 16:02:18','',NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'approved_supervisor',NULL,'2026-03-03 15:01:24','2026-03-03 15:02:18',NULL),(32,'DEM-20260303-4D303B-C',1,3,NULL,21,6,'urgent','hukybytf',2,'approved','2026-03-03 16:02:18','',NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'approved_supervisor',NULL,'2026-03-03 15:01:24','2026-03-03 15:02:18',NULL),(33,'DEM-20260304-E28A82-A',1,3,NULL,12,1,'low','',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-04 07:14:25','2026-03-04 07:14:25',NULL),(34,'DEM-20260304-E28A82-B',1,3,NULL,10,10,'low','',2,'pending',NULL,NULL,NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'supervisor_review',NULL,'2026-03-04 07:14:25','2026-03-04 07:14:25',NULL),(35,'DEM-20260304-98A384-A',1,3,NULL,12,1,'low','',2,'approved','2026-03-04 08:15:20','',NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'approved_supervisor',NULL,'2026-03-04 07:14:29','2026-03-04 07:15:20',NULL),(36,'DEM-20260304-98A384-B',1,3,NULL,10,10,'low','',2,'approved','2026-03-04 08:15:20','',NULL,'pending',NULL,NULL,NULL,0,NULL,NULL,'approved_supervisor',NULL,'2026-03-04 07:14:29','2026-03-04 07:15:20',NULL);
/*!40000 ALTER TABLE `spare_parts_demands` ENABLE KEYS */;
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
