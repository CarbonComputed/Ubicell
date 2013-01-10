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

 Date: 01/09/2013 23:10:14 PM
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
INSERT INTO `Cookie` VALUES ('1', '8a7cc45a8b8fdf1e1c433a95dc2180d8'), ('2', '4a7192358fb359d76a653e385b46558a');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
