/*
 Navicat Premium Data Transfer

 Source Server         : 127.0.0.1
 Source Server Type    : MySQL
 Source Server Version : 50525
 Source Host           : localhost
 Source Database       : ProjectTakeOver

 Target Server Type    : MySQL
 Target Server Version : 50525
 File Encoding         : utf-8

 Date: 01/09/2013 23:10:29 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `University`
-- ----------------------------
DROP TABLE IF EXISTS `University`;
CREATE TABLE `University` (
  `UID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) DEFAULT NULL,
  `NickName` varchar(255) DEFAULT NULL,
  `Mascot` varchar(255) DEFAULT NULL,
  `EmailSuffix` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT NULL,
  `State` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`UID`),
  UNIQUE KEY `UniqueUniversity` (`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `University`
-- ----------------------------
BEGIN;
INSERT INTO `University` VALUES ('1', 'Rochester Institute of Technology', 'RIT', 'Tigers', 'rit.edu', 'Rochester', 'NY');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
