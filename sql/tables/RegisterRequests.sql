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

 Date: 01/09/2013 23:10:25 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

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

SET FOREIGN_KEY_CHECKS = 1;
