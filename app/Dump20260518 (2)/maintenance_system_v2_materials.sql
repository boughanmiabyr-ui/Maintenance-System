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
-- Table structure for table `materials`
--

DROP TABLE IF EXISTS `materials`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `materials` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL,
  `name` varchar(200) NOT NULL,
  `description` text,
  `category` varchar(100) DEFAULT NULL,
  `unit` varchar(50) DEFAULT NULL,
  `min_stock` int DEFAULT '10',
  `max_stock` int DEFAULT '100',
  `current_stock` int DEFAULT '0',
  `reorder_point` int DEFAULT NULL,
  `unit_cost` decimal(10,2) DEFAULT NULL,
  `supplier` varchar(100) DEFAULT NULL,
  `supplier_id` int DEFAULT NULL,
  `last_restocked` timestamp NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `material_type` varchar(50) DEFAULT 'standard',
  `zone_id` int DEFAULT NULL,
  `machine_id` int DEFAULT NULL,
  `lifespan_days` int DEFAULT NULL,
  `stock_entry_date` datetime DEFAULT NULL,
  `stock_registration_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `idx_category` (`category`),
  KEY `idx_stock_level` (`current_stock`),
  KEY `idx_supplier_id_materials` (`supplier_id`),
  KEY `ix_materials_material_type` (`material_type`),
  KEY `zone_id` (`zone_id`),
  KEY `machine_id` (`machine_id`),
  CONSTRAINT `materials_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `materials_ibfk_2` FOREIGN KEY (`zone_id`) REFERENCES `zones` (`id`),
  CONSTRAINT `materials_ibfk_3` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=140 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materials`
--

LOCK TABLES `materials` WRITE;
/*!40000 ALTER TABLE `materials` DISABLE KEYS */;
INSERT INTO `materials` VALUES (1,'293','Ruban Jaune 50mmx33m','Par rouleau (un carton de 24 piéce)','Adhésifs','Rouleau',55,128,85,NULL,4.38,'',1,NULL,'2026-02-27 11:48:49','2026-04-13 11:03:23','standard',NULL,NULL,NULL,NULL,'2026-05-12 13:24:47'),(2,'294','Ruban Rouge 50mmx33m','Par rouleau (un carton de 24 piéce)','Adhésifs','Rouleau',10,15,6,NULL,4.33,'',1,NULL,'2026-02-27 11:48:49','2026-04-13 11:23:35','standard',NULL,NULL,NULL,NULL,'2026-05-12 13:24:47'),(3,'295','Ruban Bleu 50mmx33m','Par rouleau (un carton de 24 piéce)','Adhésifs','Rouleau',13,20,13,NULL,4.39,NULL,1,NULL,'2026-02-27 11:48:49','2026-02-27 11:48:49','standard',NULL,NULL,NULL,NULL,'2026-05-12 13:24:47'),(4,'296','Ruban Vert 50mmx33m','Par rouleau (un carton de 24 piéce)','Adhésifs','Rouleau',2,3,2,NULL,4.38,NULL,2,NULL,'2026-02-27 11:48:49','2026-02-27 11:48:49','standard',NULL,NULL,NULL,NULL,'2026-05-12 13:24:47'),(5,'297','Ruban Rouge/Blanc 50mmx33m','Par rouleau (un carton de 24 piéce)','Adhésifs','Rouleau',9,14,10,NULL,6.67,NULL,2,NULL,'2026-02-27 11:48:49','2026-02-27 11:48:49','standard',NULL,NULL,NULL,NULL,'2026-05-12 13:24:47'),(6,'545','Fusible 5*20 10AT','Fusible standard','Électrique','Pièce',1,2,1,NULL,2.14,NULL,3,NULL,'2026-02-27 11:48:49','2026-02-27 11:48:49','standard',NULL,NULL,NULL,NULL,'2026-05-12 13:24:47'),(7,'551','Fusible 5*20 6,3AT','Fusible standard','Électrique','Pièce',1,2,1,NULL,1.90,NULL,3,NULL,'2026-02-27 11:48:49','2026-02-27 11:48:49','standard',NULL,NULL,NULL,NULL,'2026-05-12 13:24:47'),(8,'553','Fusible 5x20 1AT','Fusible standard','Électrique','Pièce',1,2,1,NULL,1.96,NULL,3,NULL,'2026-02-27 11:48:49','2026-02-27 11:48:49','standard',NULL,NULL,NULL,NULL,'2026-05-12 13:24:47'),(9,'1010','Roulement rainure a billes','Roulement standard','Roulements','Pièce',1,1,1,NULL,2.92,NULL,3,NULL,'2026-02-27 11:48:49','2026-02-27 11:48:49','standard',NULL,NULL,NULL,NULL,'2026-05-12 13:24:47'),(10,'1013','Roulement rainure a bille 608-2Z','Roulement rainuré','Roulements','Pièce',3,5,2,NULL,2.95,NULL,3,NULL,'2026-02-27 11:48:49','2026-03-03 10:49:09','standard',NULL,NULL,NULL,NULL,'2026-05-12 13:24:47'),(139,'lkjhgchjkl','lkjh','kjihgfdtfyguhijokp','n,bhvgcfxfcj','kjhghj',10,100,259522,3,232.00,'lkjhgfghj',NULL,NULL,'2026-05-18 07:29:22','2026-05-18 07:29:22','standard',1,1,233,'2026-05-18 00:00:00','2026-05-18 08:29:22');
/*!40000 ALTER TABLE `materials` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-18 11:58:31
