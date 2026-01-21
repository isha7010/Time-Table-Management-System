-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: timetable
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `class`
--

DROP TABLE IF EXISTS `class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class` (
  `class_id` int NOT NULL AUTO_INCREMENT,
  `semester` int NOT NULL,
  `division` varchar(10) DEFAULT NULL,
  `student_shift_id` int DEFAULT NULL,
  `dept_id` int DEFAULT NULL,
  PRIMARY KEY (`class_id`),
  KEY `student_shift_id` (`student_shift_id`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `class_ibfk_1` FOREIGN KEY (`student_shift_id`) REFERENCES `student_shift` (`student_shift_id`),
  CONSTRAINT `class_ibfk_2` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class`
--

LOCK TABLES `class` WRITE;
/*!40000 ALTER TABLE `class` DISABLE KEYS */;
INSERT INTO `class` VALUES (1,3,'C',1,1),(2,3,'A',1,1),(3,3,'B',1,1);
/*!40000 ALTER TABLE `class` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class_subject`
--

DROP TABLE IF EXISTS `class_subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_subject` (
  `class_subject_id` int NOT NULL AUTO_INCREMENT,
  `class_id` int DEFAULT NULL,
  `subject_id` int DEFAULT NULL,
  `hours_per_week` int DEFAULT NULL,
  `faculty_id` int DEFAULT NULL,
  PRIMARY KEY (`class_subject_id`),
  KEY `class_id` (`class_id`),
  KEY `subject_id` (`subject_id`),
  KEY `fk_faculty` (`faculty_id`),
  CONSTRAINT `class_subject_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `class` (`class_id`),
  CONSTRAINT `class_subject_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`),
  CONSTRAINT `fk_faculty` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`faculty_id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_subject`
--

LOCK TABLES `class_subject` WRITE;
/*!40000 ALTER TABLE `class_subject` DISABLE KEYS */;
INSERT INTO `class_subject` VALUES (1,1,1,2,NULL),(2,1,2,4,NULL),(3,1,3,4,NULL),(4,1,4,3,NULL),(5,1,5,3,NULL),(9,3,1,2,NULL),(10,2,1,2,NULL),(11,1,1,2,NULL),(13,3,2,4,NULL),(14,2,2,4,NULL),(15,1,2,4,NULL),(17,3,3,4,NULL),(18,2,3,4,NULL),(19,1,3,4,NULL),(21,3,4,3,NULL),(22,2,4,3,NULL),(23,1,4,3,NULL),(25,3,5,3,NULL),(26,2,5,3,NULL),(27,1,5,3,NULL),(40,3,1,2,NULL),(41,2,1,2,NULL),(42,1,1,2,NULL),(44,3,2,4,NULL),(45,2,2,4,NULL),(46,1,2,4,NULL),(48,3,3,4,NULL),(49,2,3,4,NULL),(50,1,3,4,NULL),(52,3,4,3,NULL),(53,2,4,3,NULL),(54,1,4,3,NULL),(56,3,5,3,NULL),(57,2,5,3,NULL),(58,1,5,3,NULL);
/*!40000 ALTER TABLE `class_subject` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class_subject_faculty`
--

DROP TABLE IF EXISTS `class_subject_faculty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_subject_faculty` (
  `csf_id` int NOT NULL AUTO_INCREMENT,
  `class_id` int NOT NULL,
  `subject_id` int NOT NULL,
  `faculty_id` int NOT NULL,
  PRIMARY KEY (`csf_id`),
  UNIQUE KEY `class_id` (`class_id`,`subject_id`),
  KEY `subject_id` (`subject_id`),
  KEY `faculty_id` (`faculty_id`),
  CONSTRAINT `class_subject_faculty_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `class` (`class_id`),
  CONSTRAINT `class_subject_faculty_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`),
  CONSTRAINT `class_subject_faculty_ibfk_3` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`faculty_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_subject_faculty`
--

LOCK TABLES `class_subject_faculty` WRITE;
/*!40000 ALTER TABLE `class_subject_faculty` DISABLE KEYS */;
INSERT INTO `class_subject_faculty` VALUES (1,1,1,1),(2,1,6,2),(3,1,3,3),(4,1,5,4),(5,2,7,2),(6,2,5,5);
/*!40000 ALTER TABLE `class_subject_faculty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `dept_id` int NOT NULL AUTO_INCREMENT,
  `dept_name` varchar(100) NOT NULL,
  PRIMARY KEY (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES (1,'CSE Data Science');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty` (
  `faculty_id` int NOT NULL AUTO_INCREMENT,
  `faculty_name` varchar(100) NOT NULL,
  `designation` varchar(50) DEFAULT NULL,
  `max_hours_per_day` int DEFAULT NULL,
  `shift` varchar(20) DEFAULT NULL,
  `dept_id` int DEFAULT NULL,
  `max_hours_per_week` int DEFAULT '16',
  PRIMARY KEY (`faculty_id`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `faculty_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty`
--

LOCK TABLES `faculty` WRITE;
/*!40000 ALTER TABLE `faculty` DISABLE KEYS */;
INSERT INTO `faculty` VALUES (1,'Dr. A. Sharma','HOD',3,'Morning',1,16),(2,'Dr. Rupali Mahajan',NULL,3,NULL,1,18),(3,'Dr. Deepa Abin',NULL,3,NULL,1,18),(4,'Prashant Mandale',NULL,3,NULL,1,18),(5,'Keshav Tambre',NULL,3,NULL,1,18);
/*!40000 ALTER TABLE `faculty` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `faculty_shift`
--

DROP TABLE IF EXISTS `faculty_shift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `faculty_shift` (
  `faculty_shift_id` int NOT NULL AUTO_INCREMENT,
  `shift_name` varchar(20) DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  PRIMARY KEY (`faculty_shift_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `faculty_shift`
--

LOCK TABLES `faculty_shift` WRITE;
/*!40000 ALTER TABLE `faculty_shift` DISABLE KEYS */;
INSERT INTO `faculty_shift` VALUES (1,'Morning','08:00:00','14:00:00'),(2,'Evening','10:00:00','18:00:00');
/*!40000 ALTER TABLE `faculty_shift` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `room`
--

DROP TABLE IF EXISTS `room`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room` (
  `room_id` int NOT NULL AUTO_INCREMENT,
  `room_number` varchar(20) NOT NULL,
  `room_type` varchar(30) DEFAULT NULL,
  `capacity` int DEFAULT NULL,
  `dept_id` int DEFAULT NULL,
  PRIMARY KEY (`room_id`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `room_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room`
--

LOCK TABLES `room` WRITE;
/*!40000 ALTER TABLE `room` DISABLE KEYS */;
INSERT INTO `room` VALUES (4,'D201','Classroom',80,1),(5,'D205','Lab',30,1),(7,'D207','Lab',30,1),(9,'D206','Lab',30,1),(10,'D208','Classroom',70,1),(11,'D204','Classroom',70,1);
/*!40000 ALTER TABLE `room` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student_shift`
--

DROP TABLE IF EXISTS `student_shift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student_shift` (
  `student_shift_id` int NOT NULL AUTO_INCREMENT,
  `shift_name` varchar(20) DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  PRIMARY KEY (`student_shift_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student_shift`
--

LOCK TABLES `student_shift` WRITE;
/*!40000 ALTER TABLE `student_shift` DISABLE KEYS */;
INSERT INTO `student_shift` VALUES (1,'Morning','08:00:00','14:00:00'),(2,'Afternoon','12:00:00','18:00:00');
/*!40000 ALTER TABLE `student_shift` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subject`
--

DROP TABLE IF EXISTS `subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `subject` (
  `subject_id` int NOT NULL AUTO_INCREMENT,
  `subject_name` varchar(100) NOT NULL,
  `semester` int NOT NULL,
  `subject_type` varchar(20) DEFAULT NULL,
  `hours_per_week` int DEFAULT NULL,
  `dept_id` int DEFAULT NULL,
  PRIMARY KEY (`subject_id`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `subject_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subject`
--

LOCK TABLES `subject` WRITE;
/*!40000 ALTER TABLE `subject` DISABLE KEYS */;
INSERT INTO `subject` VALUES (1,'System Programming and Operating Systems',3,'Theory',2,1),(2,'DBMS',3,'Theory',4,1),(3,'Machine Learning',3,'Theory',4,1),(4,'Design & Analysis of Algorithms',3,'Theory',3,1),(5,'Probability & Statistics',3,'Theory',3,1),(6,'DT',3,NULL,3,1),(7,'Machine Learning',3,NULL,3,1),(8,'Probablity & Stat',3,NULL,2,1);
/*!40000 ALTER TABLE `subject` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `time_slot`
--

DROP TABLE IF EXISTS `time_slot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `time_slot` (
  `slot_id` int NOT NULL AUTO_INCREMENT,
  `slot_name` varchar(20) DEFAULT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `student_shift_id` int DEFAULT NULL,
  PRIMARY KEY (`slot_id`),
  KEY `student_shift_id` (`student_shift_id`),
  CONSTRAINT `time_slot_ibfk_1` FOREIGN KEY (`student_shift_id`) REFERENCES `student_shift` (`student_shift_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `time_slot`
--

LOCK TABLES `time_slot` WRITE;
/*!40000 ALTER TABLE `time_slot` DISABLE KEYS */;
INSERT INTO `time_slot` VALUES (1,'8-9','08:00:00','09:00:00',1),(2,'9-10','09:00:00','10:00:00',1),(3,'10-11','10:00:00','11:00:00',1),(4,'11-12','11:00:00','12:00:00',1),(5,'12-1','12:00:00','13:00:00',1),(6,'1-2','13:00:00','14:00:00',1),(7,'12-1','12:00:00','13:00:00',2),(8,'12-1','12:00:00','13:00:00',2),(9,'2-3','14:00:00','15:00:00',2),(10,'3-4','15:00:00','16:00:00',2),(11,'4-5','16:00:00','17:00:00',2),(12,'5-6','17:00:00','18:00:00',2);
/*!40000 ALTER TABLE `time_slot` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `role` enum('admin','faculty','student') NOT NULL,
  `linked_id` int DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin123','admin',NULL),(2,'f1','f123','faculty',1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `weekly_timetable`
--

DROP TABLE IF EXISTS `weekly_timetable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weekly_timetable` (
  `timetable_id` int NOT NULL AUTO_INCREMENT,
  `class_id` int DEFAULT NULL,
  `subject_id` int DEFAULT NULL,
  `faculty_id` int DEFAULT NULL,
  `slot_id` int DEFAULT NULL,
  `day` enum('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday') DEFAULT NULL,
  `room_id` int DEFAULT NULL,
  PRIMARY KEY (`timetable_id`),
  KEY `class_id` (`class_id`),
  KEY `subject_id` (`subject_id`),
  KEY `faculty_id` (`faculty_id`),
  KEY `slot_id` (`slot_id`),
  KEY `room_id` (`room_id`),
  CONSTRAINT `weekly_timetable_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `class` (`class_id`),
  CONSTRAINT `weekly_timetable_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`subject_id`),
  CONSTRAINT `weekly_timetable_ibfk_3` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`faculty_id`),
  CONSTRAINT `weekly_timetable_ibfk_4` FOREIGN KEY (`slot_id`) REFERENCES `time_slot` (`slot_id`),
  CONSTRAINT `weekly_timetable_ibfk_5` FOREIGN KEY (`room_id`) REFERENCES `room` (`room_id`)
) ENGINE=InnoDB AUTO_INCREMENT=424 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `weekly_timetable`
--

LOCK TABLES `weekly_timetable` WRITE;
/*!40000 ALTER TABLE `weekly_timetable` DISABLE KEYS */;
INSERT INTO `weekly_timetable` VALUES (406,1,1,1,1,'Monday',NULL),(407,1,1,1,1,'Tuesday',NULL),(408,1,3,3,2,'Tuesday',NULL),(409,1,3,3,1,'Wednesday',NULL),(410,1,3,3,1,'Thursday',NULL),(411,1,3,3,1,'Friday',NULL),(412,1,5,4,2,'Friday',NULL),(413,1,5,4,1,'Monday',NULL),(414,1,5,4,1,'Tuesday',NULL),(415,1,6,2,2,'Tuesday',NULL),(416,1,6,2,1,'Wednesday',NULL),(417,1,6,2,1,'Thursday',NULL),(418,2,5,5,1,'Monday',NULL),(419,2,5,5,1,'Tuesday',NULL),(420,2,5,5,1,'Wednesday',NULL),(421,2,7,2,2,'Wednesday',NULL),(422,2,7,2,2,'Thursday',NULL),(423,2,7,2,1,'Friday',NULL);
/*!40000 ALTER TABLE `weekly_timetable` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-22  0:17:42
