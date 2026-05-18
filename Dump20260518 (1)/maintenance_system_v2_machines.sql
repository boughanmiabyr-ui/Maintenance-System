CREATE DATABASE  IF NOT EXISTS `maintenance_system_v2` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `maintenance_system_v2`;
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
-- Table structure for table `machines`
--

DROP TABLE IF EXISTS `machines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `machines` (
  `id` int NOT NULL AUTO_INCREMENT,
  `machine_code` varchar(50) NOT NULL,
  `name` varchar(200) DEFAULT NULL,
  `description` text,
  `location` varchar(200) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `model` varchar(100) DEFAULT NULL,
  `manufacturer` varchar(100) DEFAULT NULL,
  `purchase_date` date DEFAULT NULL,
  `installation_date` date DEFAULT NULL,
  `status` varchar(50) DEFAULT 'operational',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ip_address` varchar(50) DEFAULT NULL,
  `machine_name` varchar(200) DEFAULT NULL,
  `zone` varchar(100) DEFAULT NULL,
  `zone_id` int DEFAULT NULL,
  `operation_count` int NOT NULL DEFAULT '0',
  `conditional_maintenance_threshold` int NOT NULL DEFAULT '300000',
  `last_conditional_reset_date` datetime DEFAULT NULL,
  `last_conditional_replacement_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `machine_code` (`machine_code`),
  UNIQUE KEY `ip_address` (`ip_address`),
  KEY `idx_department` (`department`),
  KEY `idx_status` (`status`),
  KEY `idx_machines_ip_address` (`ip_address`),
  KEY `idx_machines_zone` (`zone`),
  KEY `fk_machines_zones` (`zone_id`),
  KEY `idx_operation_count` (`operation_count`),
  CONSTRAINT `fk_machines_zones` FOREIGN KEY (`zone_id`) REFERENCES `zones` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `machines`
--

LOCK TABLES `machines` WRITE;
/*!40000 ALTER TABLE `machines` DISABLE KEYS */;
INSERT INTO `machines` VALUES (1,'MACH001','komax01','Main assembly line','Cutting area','Wiring','AL-2000','Komax','2022-01-15','2022-02-01','active','2026-02-27 11:48:49','2026-05-08 10:33:50','10.114.29.241','Komax 1','Cutting area',1,0,300000,NULL,NULL),(2,'MACH002','komax02','Quality testing equipment','Cutting area','Quality Control','TS-500','Advantest','2021-06-20','2021-07-15','active','2026-02-27 11:48:49','2026-03-27 17:03:15',NULL,NULL,'Cutting area',1,0,300000,NULL,NULL),(3,'MACH003','komax03','Wire winding machine','Cutting area','Wiring','WM-300','Schleifring','2023-03-10','2023-04-01','active','2026-02-27 11:48:49','2026-03-27 17:03:15',NULL,NULL,'Cutting area',1,0,300000,NULL,NULL);
/*!40000 ALTER TABLE `machines` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-18  8:59:55
