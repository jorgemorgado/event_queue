-- MySQL dump 10.13  Distrib 5.5.43
--
-- Host: localhost    Database: event
-- ------------------------------------------------------
-- Server version	5.5.43-0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `user`
--
DROP TABLE IF EXISTS `event`.`user`;
CREATE TABLE `event`.`user` (
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(45) NOT NULL,
    `username` VARCHAR(45) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_username` (`username`)
) ENGINE=InnoDB;


--
-- Table structure for table `query`
--
DROP TABLE IF EXISTS `event`.`query`;
CREATE TABLE `event`.`query` (
    `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
    `userid` INT(11) UNSIGNED NOT NULL,
    `desc` VARCHAR(45) NOT NULL,
    `request` VARCHAR(1024) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_userid_desc` (`userid`, `desc`),
    INDEX `idx_desc` (`desc`),
    CONSTRAINT FOREIGN KEY (`userid`) REFERENCES `user`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


--
-- Table structure for table `queue`
--
DROP TABLE IF EXISTS `event`.`queue`;
CREATE TABLE `queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `source` varchar(255) NOT NULL,
  `eventid` int(11) NOT NULL DEFAULT '0',
  `lasteventid` int(11) NOT NULL DEFAULT '0',
  `type` varchar(255) NOT NULL,
  `state` varchar(255) DEFAULT NULL,
  `statetype` varchar(255) DEFAULT NULL,
  `laststate` varchar(255) DEFAULT NULL,
  `count` int(11) DEFAULT '1',
  `handled` tinyint(1) NOT NULL DEFAULT '0',
  `ipv4` int(10) unsigned DEFAULT NULL,
  `ipv6` binary(16) DEFAULT NULL,
  `hostname` varchar(255) DEFAULT NULL,
  `servicename` varchar(255) DEFAULT NULL,
  `date` varchar(30) NOT NULL,
  `time` varchar(30) NOT NULL,
  `message` text,
  PRIMARY KEY (`id`),
  KEY `ts_idx` (`ts`),
  KEY `source_idx` (`source`),
  KEY `state_idx` (`state`(1)),
  KEY `handled_idx` (`handled`),
  KEY `ipv4_idx` (`ipv4`),
  KEY `ipv6_idx` (`ipv6`),
  KEY `hostname_idx` (`hostname`),
  KEY `eventid_idx` (`source`,`eventid`)
) ENGINE=InnoDB;


--
-- Create an Event Queue User
--
CREATE USER 'qapi'@'localhost' IDENTIFIED BY 'password';
-- Allow read-write on the queue table
GRANT ALL PRIVILEGES ON event.queue TO 'qapi'@'localhost';

--
-- Create an Event Queue Web User
--
CREATE USER 'eqweb'@'localhost' IDENTIFIED BY 'password';
-- Grant read-only to the queue table
GRANT SELECT ON event.queue TO 'eqweb'@'localhost';
-- Allow read-write on the user table
GRANT ALL PRIVILEGES ON event.user TO 'eqweb'@'localhost';
-- Allow read-write on the query table
GRANT ALL PRIVILEGES ON event.query TO 'eqweb'@'localhost';

FLUSH PRIVILEGES;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- End
