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

 Date: 01/09/2013 23:10:21 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

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

SET FOREIGN_KEY_CHECKS = 1;
