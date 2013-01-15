/*
 Navicat Premium Data Transfer

 Source Server         : 127.0.0.1
 Source Server Type    : MySQL
 Source Server Version : 50529
 Source Host           : localhost
 Source Database       : ProjectTakeOver

 Target Server Type    : MySQL
 Target Server Version : 50529
 File Encoding         : utf-8

 Date: 01/15/2013 16:20:06 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `Cookie`
-- ----------------------------
DROP TABLE IF EXISTS `Cookie`;
CREATE TABLE `Cookie` (
  `UserID` int(11) DEFAULT NULL,
  `CookieVal` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `Cookie`
-- ----------------------------
BEGIN;
INSERT INTO `Cookie` VALUES ('1', 'bb42b20b4162216e00bba2669cfe83f6'), ('2', '4a7192358fb359d76a653e385b46558a'), ('3', '0');
COMMIT;

-- ----------------------------
--  Table structure for `Friend`
-- ----------------------------
DROP TABLE IF EXISTS `Friend`;
CREATE TABLE `Friend` (
  `UserID` int(11) DEFAULT NULL,
  `FriendID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `Friend`
-- ----------------------------
BEGIN;
INSERT INTO `Friend` VALUES ('1', '2'), ('2', '1');
COMMIT;

-- ----------------------------
--  Table structure for `FriendRequests`
-- ----------------------------
DROP TABLE IF EXISTS `FriendRequests`;
CREATE TABLE `FriendRequests` (
  `UserID` int(11) DEFAULT NULL,
  `FriendID` int(11) DEFAULT NULL,
  UNIQUE KEY `friendReq` (`UserID`,`FriendID`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `FriendRequests`
-- ----------------------------
BEGIN;
INSERT INTO `FriendRequests` VALUES ('1', '2'), ('2', '1');
COMMIT;

-- ----------------------------
--  Table structure for `RegisterRequests`
-- ----------------------------
DROP TABLE IF EXISTS `RegisterRequests`;
CREATE TABLE `RegisterRequests` (
  `UserID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `RegisterRequests`
-- ----------------------------
BEGIN;
INSERT INTO `RegisterRequests` VALUES ('2'), ('1');
COMMIT;

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
  UNIQUE KEY `UniqueUniversity` (`Name`,`UID`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `University`
-- ----------------------------
BEGIN;
INSERT INTO `University` VALUES ('1', 'Rochester Institute of Technology', 'RIT', 'Tigers', 'rit.edu', 'Rochester', 'NY');
COMMIT;

-- ----------------------------
--  Table structure for `UniversityUser`
-- ----------------------------
DROP TABLE IF EXISTS `UniversityUser`;
CREATE TABLE `UniversityUser` (
  `UID` int(11) DEFAULT NULL,
  `UserID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `User`
-- ----------------------------
DROP TABLE IF EXISTS `User`;
CREATE TABLE `User` (
  `UserID` int(11) NOT NULL AUTO_INCREMENT,
  `UserName` varchar(255) DEFAULT NULL,
  `Password` varchar(255) DEFAULT NULL,
  `FirstName` varchar(255) DEFAULT NULL,
  `LastName` varchar(255) DEFAULT NULL,
  `Email` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `uniqueUserName` (`UserName`,`UserID`,`Email`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `User`
-- ----------------------------
BEGIN;
INSERT INTO `User` VALUES ('1', 'kmcarbone', '32f49685a4df492bc6fc51edc9d664c2', 'Kevin', 'Carbone', 'kmc8206@rit.edu'), ('2', 'njcbone2', '6f1ed002ab5595859014ebf0951522d9', 'Nick', 'Carbone', 'njcbone@gmail.com'), ('3', 'random', '7ddf32e17a6ac5ce04a8ecbf782ca509', 'random', 'rando', 'random1212@mailinator.com');
COMMIT;

-- ----------------------------
--  Table structure for `UserReply`
-- ----------------------------
DROP TABLE IF EXISTS `UserReply`;
CREATE TABLE `UserReply` (
  `ReplyID` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` int(11) DEFAULT NULL,
  `StatusID` int(11) DEFAULT NULL,
  `ReplyMsg` varchar(80) DEFAULT NULL,
  `ReplyDate` date DEFAULT NULL,
  PRIMARY KEY (`ReplyID`),
  UNIQUE KEY `ReplyID` (`ReplyID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `UserStatus`
-- ----------------------------
DROP TABLE IF EXISTS `UserStatus`;
CREATE TABLE `UserStatus` (
  `StatusID` int(11) NOT NULL AUTO_INCREMENT,
  `UserID` int(11) DEFAULT NULL,
  `StatusMsg` varchar(80) DEFAULT NULL,
  `StatusDate` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`StatusID`),
  UNIQUE KEY `StatusID` (`StatusID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1;
