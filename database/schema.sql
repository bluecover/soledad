-- MySQL dump 10.16  Distrib 10.1.12-MariaDB, for osx10.11 (x86_64)
--
-- Host: localhost    Database: solar
-- ------------------------------------------------------
-- Server version	10.1.12-MariaDB

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
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `email` varchar(60) DEFAULT NULL,
  `password` varchar(25) DEFAULT NULL,
  `salt` varchar(8) NOT NULL DEFAULT '',
  `name` varchar(60) CHARACTER SET ucs2 NOT NULL DEFAULT '',
  `gender` int(4) DEFAULT NULL,
  `status` int(4) DEFAULT NULL,
  `session_id` varchar(16) DEFAULT NULL,
  `session_expire_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=79662 DEFAULT CHARSET=utf8 COMMENT='好规划核心账户';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `account_alias`
--

DROP TABLE IF EXISTS `account_alias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account_alias` (
  `id` int(12) NOT NULL,
  `alias` varchar(60) DEFAULT NULL,
  `reg_type` int(4) DEFAULT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `idx_alias` (`alias`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='好规划核心账户别名';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `advert_record`
--

DROP TABLE IF EXISTS `advert_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `advert_record` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `kind_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_kind` (`kind_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='好规划广告点击记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `app_banner`
--

DROP TABLE IF EXISTS `app_banner`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `app_banner` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL DEFAULT '',
  `status` char(1) NOT NULL,
  `image_url` varchar(512) NOT NULL,
  `link_url` varchar(512) NOT NULL,
  `sequence` int(11) NOT NULL DEFAULT '0',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COMMENT='App首页Banner';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `article`
--

DROP TABLE IF EXISTS `article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `article` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `type` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `status` tinyint(2) unsigned NOT NULL DEFAULT '0',
  `category` int(12) unsigned NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `publish_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `cate_index` (`type`,`category`)
) ENGINE=InnoDB AUTO_INCREMENT=10338 DEFAULT CHARSET=utf8 COMMENT='理财师文章';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `child_plan`
--

DROP TABLE IF EXISTS `child_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `child_plan` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `user_id` int(12) NOT NULL,
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10446 DEFAULT CHARSET=utf8 COMMENT='儿童险规划';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon`
--

DROP TABLE IF EXISTS `coupon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(60) NOT NULL DEFAULT '' COMMENT '礼券名称',
  `user_id` int(11) unsigned DEFAULT NULL,
  `kind_id` int(4) DEFAULT NULL,
  `package_id` int(11) unsigned DEFAULT NULL,
  `status` char(1) NOT NULL,
  `platform` int(2) NOT NULL DEFAULT '0',
  `platforms` char(32) NOT NULL DEFAULT '1,2,3',
  `product_matcher_kind_id` int(8) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `expire_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `consumed_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`,`creation_time`)
) ENGINE=InnoDB AUTO_INCREMENT=1016 DEFAULT CHARSET=utf8 COMMENT='礼券';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_package`
--

DROP TABLE IF EXISTS `coupon_package`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_package` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned DEFAULT NULL,
  `kind_id` int(4) DEFAULT NULL,
  `status` char(1) DEFAULT NULL,
  `reserved_sha1` char(40) DEFAULT NULL,
  `reserved_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `unpacked_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2006 DEFAULT CHARSET=utf8 COMMENT='礼包';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_package_investment_award`
--

DROP TABLE IF EXISTS `coupon_package_investment_award`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_package_investment_award` (
  `user_id` int(11) unsigned NOT NULL,
  `zhiwang_order_id` int(11) unsigned NOT NULL,
  `package_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`package_id`),
  UNIQUE KEY `idx_user` (`user_id`),
  UNIQUE KEY `idx_zhiwang_order` (`zhiwang_order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新手首笔投资获得礼包';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_package_investment_invitation_reward`
--

DROP TABLE IF EXISTS `coupon_package_investment_invitation_reward`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_package_investment_invitation_reward` (
  `invitation_id` int(11) unsigned NOT NULL,
  `package_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`package_id`),
  UNIQUE KEY `invitation_id` (`invitation_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='邀请新人奖励记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_package_legacy_rebate`
--

DROP TABLE IF EXISTS `coupon_package_legacy_rebate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_package_legacy_rebate` (
  `user_id` int(11) unsigned NOT NULL,
  `package_id` int(11) unsigned NOT NULL,
  `rebate_voucher_id` char(32) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`package_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='历史返现记录兼容礼包';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_package_newcomer_center`
--

DROP TABLE IF EXISTS `coupon_package_newcomer_center`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_package_newcomer_center` (
  `user_id` int(11) unsigned NOT NULL,
  `package_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`package_id`),
  UNIQUE KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新手注册获得礼包';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_package_recast_inspirator`
--

DROP TABLE IF EXISTS `coupon_package_recast_inspirator`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_package_recast_inspirator` (
  `user_id` int(11) unsigned NOT NULL,
  `zhiwang_asset_id` int(11) unsigned NOT NULL,
  `package_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`package_id`),
  UNIQUE KEY `idx_user` (`user_id`),
  UNIQUE KEY `idx_zhiwang_asset` (`zhiwang_asset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新手首笔到期获得礼包';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_package_redeem_celebration`
--

DROP TABLE IF EXISTS `coupon_package_redeem_celebration`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_package_redeem_celebration` (
  `package_id` int(11) unsigned NOT NULL,
  `user_id` int(11) unsigned NOT NULL,
  `provider_id` int(4) NOT NULL,
  `order_id` char(32) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`package_id`),
  UNIQUE KEY `idx_provider_order` (`provider_id`,`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='任意产品订单到期奖励礼包';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_package_redeem_code`
--

DROP TABLE IF EXISTS `coupon_package_redeem_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_package_redeem_code` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `redeem_code_usage_id` int(11) unsigned NOT NULL,
  `package_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='兑换码礼包';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_package_special_prize`
--

DROP TABLE IF EXISTS `coupon_package_special_prize`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_package_special_prize` (
  `user_id` int(11) unsigned NOT NULL,
  `package_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`package_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='特殊奖励礼包';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_package_sunny_world`
--

DROP TABLE IF EXISTS `coupon_package_sunny_world`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_package_sunny_world` (
  `user_id` int(11) unsigned NOT NULL,
  `package_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`package_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='系统发放礼包';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_package_xm`
--

DROP TABLE IF EXISTS `coupon_package_xm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_package_xm` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `order_id` int(11) unsigned NOT NULL,
  `package_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8 COMMENT='新结算礼包';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `coupon_usage_record`
--

DROP TABLE IF EXISTS `coupon_usage_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `coupon_usage_record` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `coupon_id` int(11) unsigned NOT NULL,
  `user_id` int(11) unsigned NOT NULL,
  `provider_id` int(4) NOT NULL,
  `order_id` varchar(32) NOT NULL,
  `status` char(1) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_provider_order` (`provider_id`,`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='礼券使用记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `download_project`
--

DROP TABLE IF EXISTS `download_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `download_project` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `display_name` varchar(90) NOT NULL,
  `bucket_name` varchar(20) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='下载分发 - 项目';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `download_release`
--

DROP TABLE IF EXISTS `download_release`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `download_release` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `project_id` int(11) unsigned NOT NULL,
  `internal_version` varchar(20) NOT NULL,
  `public_version` varchar(20) NOT NULL,
  `status` char(1) NOT NULL,
  `file_name` varchar(50) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_internal_version` (`project_id`,`internal_version`),
  UNIQUE KEY `unique_file_name` (`project_id`,`file_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COMMENT='下载分发 - 版本';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `email`
--

DROP TABLE IF EXISTS `email`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `email` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `sender` varchar(60) NOT NULL,
  `receiver` varchar(60) NOT NULL,
  `kind_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15717 DEFAULT CHARSET=utf8 COMMENT='邮件对列表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `feedback` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `contact` varchar(60) DEFAULT NULL,
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=225 DEFAULT CHARSET=utf8 COMMENT='用户反馈';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `firewood_burning`
--

DROP TABLE IF EXISTS `firewood_burning`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `firewood_burning` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `amount` decimal(20,2) NOT NULL,
  `kind` char(4) NOT NULL,
  `status` char(1) NOT NULL,
  `provider_id` tinyint(4) NOT NULL,
  `order_id` char(32) NOT NULL,
  `remote_transaction_id` char(32) NOT NULL DEFAULT '',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8 COMMENT='抵扣金消费记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `firewood_piling`
--

DROP TABLE IF EXISTS `firewood_piling`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `firewood_piling` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `amount` decimal(20,2) NOT NULL,
  `welfare_package_id` int(11) unsigned NOT NULL DEFAULT '0',
  `gather_ghat_id` int(11) unsigned NOT NULL DEFAULT '0',
  `gather_voucher_id` char(32) NOT NULL DEFAULT '',
  `remote_transaction_id` char(32) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8 COMMENT='抵扣金充值记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `funcombo_data`
--

DROP TABLE IF EXISTS `funcombo_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `funcombo_data` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `fund_code` char(6) NOT NULL,
  `day` date NOT NULL,
  `net_worth` decimal(7,4) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_fund_day` (`fund_code`,`day`)
) ENGINE=InnoDB AUTO_INCREMENT=1741 DEFAULT CHARSET=utf8 COMMENT='基金';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `funcombo_fund`
--

DROP TABLE IF EXISTS `funcombo_fund`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `funcombo_fund` (
  `code` char(6) NOT NULL,
  `name` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='基金';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `funcombo_group`
--

DROP TABLE IF EXISTS `funcombo_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `funcombo_group` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `subject` varchar(50) NOT NULL DEFAULT '',
  `subtitle` varchar(50) NOT NULL DEFAULT '',
  `subtitle2` varchar(100) NOT NULL DEFAULT '',
  `description` varchar(200) NOT NULL DEFAULT '',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `reason` varchar(200) NOT NULL DEFAULT '',
  `highlight` varchar(200) NOT NULL DEFAULT '',
  `reason_update` varchar(200) NOT NULL DEFAULT '',
  `related` varchar(200) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COMMENT='组合推荐组';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `funcombo_group_fund`
--

DROP TABLE IF EXISTS `funcombo_group_fund`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `funcombo_group_fund` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `group_id` int(11) unsigned NOT NULL,
  `fund_code` char(6) NOT NULL,
  `rate` float unsigned NOT NULL,
  `reason` varchar(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_groupfund` (`group_id`,`fund_code`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8 COMMENT='组内包含基金';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `funcombo_income`
--

DROP TABLE IF EXISTS `funcombo_income`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `funcombo_income` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `group_id` int(11) unsigned NOT NULL,
  `day` date NOT NULL,
  `income` float NOT NULL DEFAULT '0',
  `income_stock` float NOT NULL DEFAULT '0',
  `net_worth` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_income_group` (`group_id`,`day`)
) ENGINE=InnoDB AUTO_INCREMENT=369 DEFAULT CHARSET=utf8 COMMENT='组合收益历史';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `funcombo_income_user`
--

DROP TABLE IF EXISTS `funcombo_income_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `funcombo_income_user` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `group_id` int(11) unsigned NOT NULL,
  `user_id` int(11) unsigned NOT NULL,
  `day` date NOT NULL,
  `income` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_income_user` (`group_id`,`user_id`,`day`),
  KEY `idx_income_group_user` (`group_id`,`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=869 DEFAULT CHARSET=utf8 COMMENT='用户组合收益历史';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `funcombo_userlike`
--

DROP TABLE IF EXISTS `funcombo_userlike`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `funcombo_userlike` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `group_id` int(11) unsigned NOT NULL,
  `user_id` int(11) unsigned NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `start_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_user_like` (`group_id`,`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8 COMMENT='用户关注组合';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_bankcard`
--

DROP TABLE IF EXISTS `hoard_bankcard`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_bankcard` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `user_id` int(12) NOT NULL,
  `card_number_sha1` varchar(40) NOT NULL,
  `bank_id_sha1` varchar(40) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` char(1) NOT NULL DEFAULT 'A',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_hoard_bankcard_card` (`card_number_sha1`,`status`)
) ENGINE=InnoDB AUTO_INCREMENT=25642 DEFAULT CHARSET=utf8 COMMENT='攒钱:银行卡';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_order`
--

DROP TABLE IF EXISTS `hoard_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_order` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `service_id` varchar(32) NOT NULL,
  `user_id` int(12) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fin_order_id` varchar(32) DEFAULT NULL,
  `order_amount` decimal(20,10) NOT NULL,
  `order_id` varchar(32) DEFAULT NULL,
  `bankcard_id` int(12) DEFAULT NULL,
  `status` char(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_hoard_fin_order_id` (`fin_order_id`),
  UNIQUE KEY `idx_hoard_order_id` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=198246 DEFAULT CHARSET=utf8 COMMENT='攒钱:订单';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_placebo_order`
--

DROP TABLE IF EXISTS `hoard_placebo_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_placebo_order` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned NOT NULL,
  `product_id` int(10) unsigned NOT NULL,
  `bankcard_id` int(10) unsigned NOT NULL,
  `amount` decimal(20,10) unsigned NOT NULL,
  `annual_rate_hike` decimal(20,10) unsigned NOT NULL,
  `status` int(10) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='攒钱助手体验金-订单';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_placebo_product`
--

DROP TABLE IF EXISTS `hoard_placebo_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_placebo_product` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `strategy_id` int(10) unsigned NOT NULL,
  `min_amount` decimal(20,10) NOT NULL,
  `max_amount` decimal(20,10) NOT NULL,
  `start_sell_date` date NOT NULL,
  `end_sell_date` date NOT NULL,
  `frozen_days` int(10) unsigned NOT NULL,
  `annual_rate` decimal(20,10) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='攒钱助手体验金-产品';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_profile`
--

DROP TABLE IF EXISTS `hoard_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_profile` (
  `account_id` int(12) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='攒钱:个人信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_rebate`
--

DROP TABLE IF EXISTS `hoard_rebate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_rebate` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `user_id` int(12) NOT NULL,
  `order_id` varchar(32) NOT NULL,
  `order_amount` decimal(20,10) NOT NULL,
  `rebate_amount` decimal(20,10) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `settled_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `type` int(4) NOT NULL,
  `is_settled` tinyint(1) NOT NULL DEFAULT '0',
  `order_pk` int(12) NOT NULL DEFAULT '0',
  `is_deleted` tinyint(1) NOT NULL DEFAULT '0',
  `reason` varchar(500) NOT NULL DEFAULT '',
  `withdraw_id` int(12) DEFAULT NULL,
  `activity_id` int(12) NOT NULL DEFAULT '0' COMMENT '活动id',
  PRIMARY KEY (`id`),
  KEY `idx_by_user_id` (`user_id`,`is_settled`),
  KEY `idx_hoard_rebate_type_and_order` (`order_id`,`type`)
) ENGINE=InnoDB AUTO_INCREMENT=25748 DEFAULT CHARSET=utf8 COMMENT='攒钱:返利';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_withdraw`
--

DROP TABLE IF EXISTS `hoard_withdraw`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_withdraw` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `user_id` int(12) DEFAULT NULL,
  `local_biz_id` varchar(32) DEFAULT NULL,
  `transaction_id` varchar(32) DEFAULT NULL,
  `withdraw_amount` decimal(20,10) NOT NULL,
  `bankcard_id` int(12) DEFAULT NULL,
  `status` int(4) DEFAULT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `pay_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_hoard_withdraw` (`local_biz_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13828 DEFAULT CHARSET=utf8 COMMENT='宜信返现';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_xm_account`
--

DROP TABLE IF EXISTS `hoard_xm_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_xm_account` (
  `account_id` int(11) NOT NULL,
  `xm_id` char(32) NOT NULL,
  `bind_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新米-账号绑定';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_xm_asset`
--

DROP TABLE IF EXISTS `hoard_xm_asset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_xm_asset` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `asset_no` char(32) NOT NULL,
  `order_code` char(32) NOT NULL,
  `bankcard_id` int(11) NOT NULL DEFAULT '0',
  `bank_account` char(32) NOT NULL,
  `product_id` varchar(32) NOT NULL,
  `user_id` int(11) NOT NULL,
  `remote_status` char(2) NOT NULL DEFAULT '00',
  `status` char(1) NOT NULL DEFAULT '',
  `annual_rate` decimal(20,10) NOT NULL,
  `actual_annual_rate` decimal(20,10) NOT NULL DEFAULT '0.0000000000',
  `create_amount` decimal(20,10) NOT NULL,
  `current_amount` decimal(20,10) NOT NULL,
  `base_interest` decimal(20,10) NOT NULL,
  `expect_interest` decimal(20,10) NOT NULL,
  `current_interest` decimal(20,10) NOT NULL,
  `interest_start_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `interest_end_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `expect_payback_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `buy_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_asset_no` (`asset_no`),
  UNIQUE KEY `idx_order_code` (`order_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新米-资产';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_xm_loan`
--

DROP TABLE IF EXISTS `hoard_xm_loan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_xm_loan` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `loans_digest_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `‘index_loans_digest_id’` (`loans_digest_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新米资产借贷人信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_xm_loans_digest`
--

DROP TABLE IF EXISTS `hoard_xm_loans_digest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_xm_loans_digest` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `asset_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_asset_id` (`asset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新米资产借贷信息摘要';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_xm_order`
--

DROP TABLE IF EXISTS `hoard_xm_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_xm_order` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` varchar(32) NOT NULL,
  `bankcard_id` int(11) NOT NULL,
  `amount` decimal(20,10) NOT NULL,
  `pay_amount` decimal(20,10) NOT NULL,
  `expect_interest` decimal(20,10) NOT NULL,
  `start_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `due_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `order_code` varchar(32) DEFAULT NULL,
  `pay_code` varchar(32) DEFAULT NULL,
  `remote_status` char(2) NOT NULL DEFAULT '00',
  `status` char(1) NOT NULL DEFAULT '',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_xm_order_code` (`order_code`),
  UNIQUE KEY `idx_xm_pay_code` (`pay_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新米-订单';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_xm_product`
--

DROP TABLE IF EXISTS `hoard_xm_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_xm_product` (
  `product_id` varchar(32) NOT NULL,
  `product_type` int(11) DEFAULT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `start_sell_date` date NOT NULL DEFAULT '0000-00-00',
  `end_sell_date` date NOT NULL DEFAULT '0000-00-00',
  PRIMARY KEY (`product_id`),
  KEY `idx_date` (`start_sell_date`,`end_sell_date`,`creation_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新米-产品';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_xm_profile`
--

DROP TABLE IF EXISTS `hoard_xm_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_xm_profile` (
  `account_id` int(11) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新米:个人信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_xm_profit_hike`
--

DROP TABLE IF EXISTS `hoard_xm_profit_hike`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_xm_profit_hike` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `kind` char(4) NOT NULL,
  `status` char(1) NOT NULL,
  `annual_rate_offset` decimal(20,10) NOT NULL,
  `deduct_amount` decimal(20,10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `index_order_and_kind` (`order_id`,`kind`)
) ENGINE=InnoDB AUTO_INCREMENT=7410 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_yixin_account`
--

DROP TABLE IF EXISTS `hoard_yixin_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_yixin_account` (
  `account_id` int(12) NOT NULL,
  `p2p_account` varchar(32) NOT NULL,
  `p2p_token` varchar(32) NOT NULL,
  PRIMARY KEY (`account_id`),
  UNIQUE KEY `idx_p2p_account` (`p2p_account`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='攒钱:宜定盈授权';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_yixin_service`
--

DROP TABLE IF EXISTS `hoard_yixin_service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_yixin_service` (
  `uuid` varchar(32) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='攒钱:宜定盈服务';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_zhiwang_account`
--

DROP TABLE IF EXISTS `hoard_zhiwang_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_zhiwang_account` (
  `account_id` int(11) NOT NULL,
  `zhiwang_id` char(32) NOT NULL,
  `bind_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='指旺-账号绑定';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_zhiwang_asset`
--

DROP TABLE IF EXISTS `hoard_zhiwang_asset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_zhiwang_asset` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `asset_no` char(32) NOT NULL,
  `order_code` char(32) NOT NULL,
  `bankcard_id` int(11) NOT NULL DEFAULT '0',
  `bank_account` char(32) NOT NULL,
  `product_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `status` char(1) NOT NULL DEFAULT '',
  `annual_rate` decimal(20,10) NOT NULL,
  `actual_annual_rate` decimal(20,10) NOT NULL DEFAULT '0.0000000000',
  `create_amount` decimal(20,10) NOT NULL,
  `current_amount` decimal(20,10) NOT NULL,
  `base_interest` decimal(20,10) NOT NULL,
  `expect_interest` decimal(20,10) NOT NULL,
  `current_interest` decimal(20,10) NOT NULL,
  `interest_start_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `interest_end_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `expect_payback_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `buy_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_asset_no` (`asset_no`),
  UNIQUE KEY `idx_order_code` (`order_code`)
) ENGINE=InnoDB AUTO_INCREMENT=28363 DEFAULT CHARSET=utf8 COMMENT='指旺-资产';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_zhiwang_loan`
--

DROP TABLE IF EXISTS `hoard_zhiwang_loan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_zhiwang_loan` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `loans_digest_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `‘index_loans_digest_id’` (`loans_digest_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='指旺资产借贷人信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_zhiwang_loans_digest`
--

DROP TABLE IF EXISTS `hoard_zhiwang_loans_digest`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_zhiwang_loans_digest` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `asset_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_asset_id` (`asset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='指旺资产借贷信息摘要';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_zhiwang_order`
--

DROP TABLE IF EXISTS `hoard_zhiwang_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_zhiwang_order` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `wrapped_product_id` int(11) DEFAULT NULL,
  `bankcard_id` int(11) NOT NULL,
  `amount` decimal(20,10) NOT NULL,
  `pay_amount` decimal(20,10) NOT NULL,
  `expect_interest` decimal(20,10) NOT NULL,
  `start_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `due_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `order_code` varchar(32) DEFAULT NULL,
  `pay_code` varchar(32) DEFAULT NULL,
  `status` char(1) NOT NULL DEFAULT '',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_zhiwang_order_code` (`order_code`),
  UNIQUE KEY `idx_zhiwang_pay_code` (`pay_code`),
  KEY `index_create_time` (`creation_time`),
  KEY `index_status` (`status`)
) ENGINE=InnoDB AUTO_INCREMENT=37762 DEFAULT CHARSET=utf8 COMMENT='指旺-订单';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_zhiwang_product`
--

DROP TABLE IF EXISTS `hoard_zhiwang_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_zhiwang_product` (
  `product_id` int(11) unsigned NOT NULL,
  `product_type` varchar(32) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `start_sell_date` date NOT NULL DEFAULT '0000-00-00',
  `end_sell_date` date NOT NULL DEFAULT '0000-00-00',
  PRIMARY KEY (`product_id`),
  KEY `idx_date` (`start_sell_date`,`end_sell_date`,`creation_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='指旺-产品';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_zhiwang_profile`
--

DROP TABLE IF EXISTS `hoard_zhiwang_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_zhiwang_profile` (
  `account_id` int(11) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='指旺:个人信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_zhiwang_profit_hike`
--

DROP TABLE IF EXISTS `hoard_zhiwang_profit_hike`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_zhiwang_profit_hike` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `kind` char(4) NOT NULL,
  `status` char(1) NOT NULL,
  `annual_rate_offset` decimal(20,10) NOT NULL,
  `deduct_amount` decimal(20,10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `index_order_and_kind` (`order_id`,`kind`)
) ENGINE=InnoDB AUTO_INCREMENT=7350 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoard_zhiwang_wrapped_product`
--

DROP TABLE IF EXISTS `hoard_zhiwang_wrapped_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoard_zhiwang_wrapped_product` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `kind_id` int(11) unsigned NOT NULL,
  `raw_product_id` int(11) unsigned NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_wrapped_product_composition` (`kind_id`,`raw_product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=105 DEFAULT CHARSET=utf8 COMMENT='指旺-子产品';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoarder_account`
--

DROP TABLE IF EXISTS `hoarder_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoarder_account` (
  `account_id` int(11) unsigned NOT NULL,
  `remote_id` char(32) NOT NULL,
  `status` char(1) NOT NULL,
  `bind_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `vendor_id` int(11) unsigned NOT NULL,
  PRIMARY KEY (`account_id`),
  KEY `idx_vendor_id` (`vendor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='账号绑定';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoarder_asset`
--

DROP TABLE IF EXISTS `hoarder_asset`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoarder_asset` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `status` char(1) NOT NULL,
  `remote_status` char(2) NOT NULL DEFAULT '00',
  `asset_no` char(32) DEFAULT NULL,
  `order_code` char(32) DEFAULT NULL,
  `bankcard_id` int(11) NOT NULL DEFAULT '0',
  `bank_account` char(32) NOT NULL,
  `annual_rate` decimal(20,10) NOT NULL,
  `create_amount` decimal(20,10) NOT NULL,
  `current_amount` decimal(20,10) NOT NULL,
  `fixed_service_fee` decimal(20,10) NOT NULL,
  `service_fee_rate` decimal(20,10) NOT NULL,
  `base_interest` decimal(20,10) NOT NULL,
  `expect_interest` decimal(20,10) NOT NULL,
  `current_interest` decimal(20,10) NOT NULL,
  `interest_start_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `interest_end_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `expect_payback_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `buy_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoarder_bankcard_binding`
--

DROP TABLE IF EXISTS `hoarder_bankcard_binding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoarder_bankcard_binding` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `bankcard_id` int(11) unsigned NOT NULL,
  `vendor_id` int(11) unsigned NOT NULL,
  `is_confirmed` tinyint(1) NOT NULL DEFAULT '0',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='hoarder银行卡绑定';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoarder_order`
--

DROP TABLE IF EXISTS `hoarder_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoarder_order` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `product_id` int(11) unsigned NOT NULL,
  `bankcard_id` int(11) unsigned NOT NULL,
  `amount` decimal(20,10) NOT NULL,
  `pay_amount` decimal(20,10) NOT NULL,
  `expect_interest` decimal(20,10) NOT NULL,
  `order_code` varchar(32) NOT NULL,
  `pay_code` varchar(32) DEFAULT NULL,
  `direction` char(1) NOT NULL DEFAULT 'S',
  `status` char(1) NOT NULL,
  `remote_status` char(2) NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `due_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1000 DEFAULT CHARSET=utf8 COMMENT='订单';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoarder_order_gift_usage_record`
--

DROP TABLE IF EXISTS `hoarder_order_gift_usage_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoarder_order_gift_usage_record` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `product_id` int(11) unsigned NOT NULL,
  `order_id` int(11) unsigned NOT NULL,
  `effective_amount` decimal(20,10) NOT NULL,
  `gift_type` char(1) NOT NULL,
  `status` char(1) NOT NULL,
  `effective_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `end_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_order` (`product_id`,`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='产品使用优惠记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoarder_product`
--

DROP TABLE IF EXISTS `hoarder_product`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoarder_product` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `vendor_id` int(11) unsigned NOT NULL,
  `remote_id` varchar(32) NOT NULL,
  `type` char(1) NOT NULL,
  `status` char(1) NOT NULL,
  `min_amount` decimal(20,10) NOT NULL,
  `max_amount` decimal(20,10) NOT NULL,
  `rate_type` int(11) NOT NULL,
  `rate` decimal(20,10) NOT NULL,
  `effect_day_condition` char(1) NOT NULL,
  `effect_day` int(11) NOT NULL,
  `effect_day_unit` char(1) NOT NULL,
  `redeem_type` char(1) NOT NULL,
  `start_sell_date` date NOT NULL DEFAULT '0000-00-00',
  `end_sell_date` date NOT NULL DEFAULT '0000-00-00',
  `update_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `kind` char(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `vendor_product_kind` (`vendor_id`,`remote_id`,`kind`),
  KEY `idx_date` (`start_sell_date`,`end_sell_date`,`creation_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='产品';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `hoarder_vendor`
--

DROP TABLE IF EXISTS `hoarder_vendor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `hoarder_vendor` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `protocol` char(32) NOT NULL,
  `status` char(1) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10000 DEFAULT CHARSET=utf8 COMMENT='合作方信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `insurance`
--

DROP TABLE IF EXISTS `insurance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `insurance` (
  `kind` int(5) unsigned NOT NULL DEFAULT '0',
  `insurance_id` int(5) unsigned NOT NULL DEFAULT '0',
  `name` varchar(60) DEFAULT NULL,
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `rec_rank` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`insurance_id`),
  KEY `idx_kind` (`kind`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='保险条目表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `insurance_61`
--

DROP TABLE IF EXISTS `insurance_61`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `insurance_61` (
  `account_id` int(12) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='在61推广活动中保险个人信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `insurance_package`
--

DROP TABLE IF EXISTS `insurance_package`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `insurance_package` (
  `package_id` int(5) unsigned NOT NULL DEFAULT '0',
  `pkg_name` varchar(60) DEFAULT NULL,
  `insurance_id` int(5) unsigned NOT NULL DEFAULT '0',
  `insurance_name` varchar(60) DEFAULT NULL,
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `rec_rank_in_package` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `package_rec_rank` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`package_id`,`insurance_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='保险套餐表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `insurance_plan`
--

DROP TABLE IF EXISTS `insurance_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `insurance_plan` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `user_id` int(12) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户保险规划表单';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `insurance_profile`
--

DROP TABLE IF EXISTS `insurance_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `insurance_profile` (
  `account_id` int(12) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='保险个人信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `invitation`
--

DROP TABLE IF EXISTS `invitation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `invitation` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `invitee_id` int(11) unsigned NOT NULL,
  `inviter_id` int(11) unsigned NOT NULL,
  `kind` int(11) unsigned NOT NULL,
  `status` char(1) NOT NULL,
  `expire_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `invitee_id` (`invitee_id`),
  KEY `index_inviter_id` (`inviter_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='邀请新人活动记录表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `location`
--

DROP TABLE IF EXISTS `location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `location` (
  `id` int(12) NOT NULL,
  `name_cn` varchar(50) CHARACTER SET ucs2 NOT NULL,
  `parent_id` int(12) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='城市信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `lottery_gift`
--

DROP TABLE IF EXISTS `lottery_gift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lottery_gift` (
  `id` int(12) NOT NULL,
  `name` varchar(25) NOT NULL DEFAULT '',
  `num` int(11) NOT NULL DEFAULT '0',
  `last` int(11) NOT NULL DEFAULT '0',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='抽奖奖品';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notification`
--

DROP TABLE IF EXISTS `notification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notification` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `kind_id` int(8) NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `read_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8 COMMENT='消息通知';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oauth_client`
--

DROP TABLE IF EXISTS `oauth_client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oauth_client` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `client_id` char(30) NOT NULL DEFAULT '',
  `client_secret` char(30) NOT NULL DEFAULT '',
  `redirect_uri` varchar(255) NOT NULL DEFAULT '',
  `allowed_grant_types` varchar(255) DEFAULT '',
  `allowed_response_types` varchar(255) DEFAULT '',
  `allowed_scopes` varchar(255) DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `client_id` (`client_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COMMENT='OAuth Provider Client';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oauth_grant`
--

DROP TABLE IF EXISTS `oauth_grant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oauth_grant` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `client_id` int(11) unsigned NOT NULL,
  `code` char(30) NOT NULL DEFAULT '',
  `user_id` int(11) unsigned NOT NULL,
  `scopes` varchar(255) NOT NULL DEFAULT '',
  `redirect_uri` varchar(255) NOT NULL DEFAULT '',
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `oauth_grant_client_code` (`client_id`,`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='OAuth Provider Grant Token';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `oauth_token`
--

DROP TABLE IF EXISTS `oauth_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `oauth_token` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `client_id` int(11) unsigned NOT NULL,
  `user_id` int(11) unsigned NOT NULL,
  `access_token` char(30) NOT NULL DEFAULT '',
  `refresh_token` char(30) NOT NULL DEFAULT '',
  `scopes` varchar(255) NOT NULL DEFAULT '',
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_frozen` tinyint(1) NOT NULL,
  `expires_in` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `access_token` (`access_token`),
  UNIQUE KEY `refresh_token` (`refresh_token`)
) ENGINE=InnoDB AUTO_INCREMENT=3977 DEFAULT CHARSET=utf8 COMMENT='OAuth Provider Bearer Token';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `product_bank_financial`
--

DROP TABLE IF EXISTS `product_bank_financial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `product_bank_financial` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET ucs2 NOT NULL,
  `type` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `risk_rank` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `earning` float NOT NULL DEFAULT '0',
  `min_money` int(12) NOT NULL DEFAULT '0',
  `start_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `end_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `rec_rank` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='银行理财';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `product_debt`
--

DROP TABLE IF EXISTS `product_debt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `product_debt` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET ucs2 NOT NULL,
  `type` int(5) unsigned NOT NULL DEFAULT '0',
  `risk_rank` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `rate` float NOT NULL DEFAULT '0',
  `duration` int(12) unsigned NOT NULL DEFAULT '0',
  `min_money` int(12) NOT NULL DEFAULT '0',
  `pay_type` int(5) unsigned NOT NULL DEFAULT '0',
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `rec_rank` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='债券';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `product_fund`
--

DROP TABLE IF EXISTS `product_fund`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `product_fund` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `type` int(5) unsigned NOT NULL DEFAULT '0',
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `rec_rank` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10015 DEFAULT CHARSET=utf8 COMMENT='基金';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `product_insure`
--

DROP TABLE IF EXISTS `product_insure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `product_insure` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `type` int(5) unsigned NOT NULL DEFAULT '0',
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `rec_rank` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10036 DEFAULT CHARSET=utf8 COMMENT='保险';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `product_p2p`
--

DROP TABLE IF EXISTS `product_p2p`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `product_p2p` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `type` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `rec_rank` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10006 DEFAULT CHARSET=utf8 COMMENT='P2P';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `profile_address`
--

DROP TABLE IF EXISTS `profile_address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `profile_address` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `division_id` char(6) NOT NULL DEFAULT '' COMMENT 'GB2260 行政区域代码',
  `street` varchar(255) NOT NULL DEFAULT '',
  `receiver_name` varchar(60) DEFAULT '',
  `receiver_phone` varchar(20) DEFAULT '',
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=654 DEFAULT CHARSET=utf8 COMMENT='用户地址';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `profile_identity`
--

DROP TABLE IF EXISTS `profile_identity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `profile_identity` (
  `id` int(11) unsigned NOT NULL,
  `person_name` varchar(60) NOT NULL DEFAULT '' COMMENT '真实姓名',
  `person_ricn` char(18) NOT NULL DEFAULT '' COMMENT '身份证号',
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户身份信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `promotion_christmas_2015`
--

DROP TABLE IF EXISTS `promotion_christmas_2015`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `promotion_christmas_2015` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `mobile_phone` varchar(11) NOT NULL DEFAULT '',
  `rank` int(11) unsigned NOT NULL,
  `is_awarded` tinyint(1) NOT NULL,
  `awarded_package_id` int(11) unsigned NOT NULL DEFAULT '0',
  `updated_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `created_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `mobile_phone` (`mobile_phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='2015 圣诞节烤蛋糕小游戏';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `promotion_spring_2016`
--

DROP TABLE IF EXISTS `promotion_spring_2016`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `promotion_spring_2016` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `mobile_phone` varchar(11) NOT NULL DEFAULT '',
  `status` char(1) NOT NULL DEFAULT '',
  `order_id` int(11) unsigned DEFAULT NULL,
  `user_id` int(11) unsigned DEFAULT NULL,
  `reserved_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `obtained_time` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  `upgraded_time` timestamp NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `mobile_phone` (`mobile_phone`),
  UNIQUE KEY `user_id` (`user_id`),
  UNIQUE KEY `order_id` (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='2016 春节活动: 攒钱送体验金';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pusher_device_binding`
--

DROP TABLE IF EXISTS `pusher_device_binding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pusher_device_binding` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `device_id` varchar(32) NOT NULL,
  `status` char(1) NOT NULL,
  `platform` tinyint(2) NOT NULL,
  `app_version` char(32) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_id` (`device_id`),
  KEY `user_index` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=utf8 COMMENT='极光推送设备';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pusher_group_record`
--

DROP TABLE IF EXISTS `pusher_group_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pusher_group_record` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `notification_kind_id` int(8) NOT NULL,
  `subdivision_kind_id` int(8) unsigned DEFAULT NULL,
  `is_pushed` tinyint(1) NOT NULL,
  `jmsg_id` char(32) NOT NULL DEFAULT '',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `push_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8 COMMENT='通知推送组播记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pusher_universe_record`
--

DROP TABLE IF EXISTS `pusher_universe_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pusher_universe_record` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `bulletin_id` int(11) unsigned NOT NULL,
  `is_pushed` tinyint(1) NOT NULL,
  `jmsg_id` char(32) NOT NULL DEFAULT '',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `push_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `bulletin_index` (`bulletin_id`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8 COMMENT='通知推送广播记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pusher_user_record`
--

DROP TABLE IF EXISTS `pusher_user_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pusher_user_record` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `device_id` varchar(32) NOT NULL,
  `notification_id` int(11) unsigned NOT NULL,
  `status` char(1) NOT NULL,
  `jmsg_id` char(32) NOT NULL DEFAULT '',
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `push_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `received_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `clicked_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `device_notification` (`device_id`,`notification_id`),
  KEY `user_index` (`user_id`),
  KEY `jmsg_index` (`jmsg_id`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8 COMMENT='通知推送单播记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `redeem_code`
--

DROP TABLE IF EXISTS `redeem_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `redeem_code` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(10) NOT NULL,
  `activity_id` int(11) unsigned NOT NULL,
  `source` char(1) NOT NULL,
  `max_usage_limit_per_code` int(10) NOT NULL,
  `kind` int(10) NOT NULL,
  `status` char(1) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `effective_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `expire_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='兑换码表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `redeem_code_usage`
--

DROP TABLE IF EXISTS `redeem_code_usage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `redeem_code_usage` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `code_id` int(11) unsigned NOT NULL,
  `user_id` int(11) unsigned NOT NULL,
  `activity_id` int(11) unsigned NOT NULL,
  `consumed_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_id` (`code_id`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='兑换码使用表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `security_twofactor`
--

DROP TABLE IF EXISTS `security_twofactor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `security_twofactor` (
  `id` int(11) unsigned NOT NULL COMMENT '用户 ID',
  `secret_key` binary(20) NOT NULL COMMENT 'TOTP 密钥',
  `is_enabled` tinyint(1) NOT NULL COMMENT '是否已启用',
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='安全 - 两步认证';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `shorten_url`
--

DROP TABLE IF EXISTS `shorten_url`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `shorten_url` (
  `code` varchar(8) NOT NULL,
  `confuse` varchar(19) NOT NULL,
  `url` varchar(512) NOT NULL,
  UNIQUE KEY `idx_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='短网址服务';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `site_announcement`
--

DROP TABLE IF EXISTS `site_announcement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `site_announcement` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `subject_type` char(1) NOT NULL,
  `content_type` char(1) NOT NULL,
  `status` char(1) NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `stop_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `endpoint` varchar(20) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `time_range` (`start_time`,`stop_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='站点通知';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `site_bulletin`
--

DROP TABLE IF EXISTS `site_bulletin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `site_bulletin` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `title_content_sha1` varchar(40) NOT NULL,
  `platforms` char(32) NOT NULL,
  `cast_kind` char(1) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `expire_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_tc_sha1` (`title_content_sha1`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8 COMMENT='APP运营布告';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_channel`
--

DROP TABLE IF EXISTS `user_channel`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_channel` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL DEFAULT '',
  `tag` varchar(21) NOT NULL DEFAULT '',
  `is_enabled` tinyint(1) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `tag` (`tag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户注册的商务渠道';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_channel_register`
--

DROP TABLE IF EXISTS `user_channel_register`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_channel_register` (
  `user_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `channel_id` int(11) unsigned NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_id` (`user_id`,`channel_id`),
  KEY `channel_id` (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户和商务渠道的对应关系';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_lottery`
--

DROP TABLE IF EXISTS `user_lottery`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_lottery` (
  `user_id` int(12) NOT NULL,
  `remain_num` int(11) DEFAULT NULL,
  `used_num` int(11) DEFAULT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  KEY `FK_ID` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户抽奖次数';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_lottery_num`
--

DROP TABLE IF EXISTS `user_lottery_num`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_lottery_num` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `user_id` int(12) NOT NULL,
  `get_type` int(12) NOT NULL,
  `lottery_num` int(12) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户抽奖记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_lottery_record`
--

DROP TABLE IF EXISTS `user_lottery_record`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_lottery_record` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `user_id` int(12) NOT NULL,
  `gift_id` int(12) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户抽奖记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_plan`
--

DROP TABLE IF EXISTS `user_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_plan` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `user_id` int(12) NOT NULL,
  `step` tinyint(4) unsigned NOT NULL DEFAULT '1',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26085 DEFAULT CHARSET=utf8 COMMENT='用户规划书表单';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_report`
--

DROP TABLE IF EXISTS `user_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_report` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `confuse_name` varchar(30) DEFAULT NULL,
  `plan_id` int(12) NOT NULL,
  `rev` varchar(64) NOT NULL,
  `formula_ver` varchar(20) NOT NULL,
  `status` tinyint(4) NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_confuse_name` (`confuse_name`),
  KEY `idx_plan` (`plan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=42138 DEFAULT CHARSET=utf8 COMMENT='用户规划书报表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_tag`
--

DROP TABLE IF EXISTS `user_tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_tag` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `tag` varchar(32) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  KEY `tag_index` (`tag`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=utf8 COMMENT='极光推送标签';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_verify`
--

DROP TABLE IF EXISTS `user_verify`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_verify` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) DEFAULT NULL,
  `code_type` int(11) DEFAULT NULL,
  `verify_code` varchar(255) DEFAULT NULL,
  `created_time` datetime DEFAULT NULL,
  `verify_time` datetime DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`,`verify_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=95978 DEFAULT CHARSET=utf8 COMMENT='用户验证表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wallet_account`
--

DROP TABLE IF EXISTS `wallet_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wallet_account` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `account_id` int(11) NOT NULL,
  `provider_id` int(11) NOT NULL,
  `secret_token` char(32) NOT NULL DEFAULT '',
  `status_code` char(1) NOT NULL,
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `wallet_account_provider` (`account_id`,`provider_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1052 DEFAULT CHARSET=utf8 COMMENT='零钱包-账户信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wallet_annual_rate`
--

DROP TABLE IF EXISTS `wallet_annual_rate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wallet_annual_rate` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `annual_rate` decimal(20,10) NOT NULL,
  `ttp_income` decimal(20,10) NOT NULL,
  `fund_code` varchar(11) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `date` (`date`,`fund_code`)
) ENGINE=InnoDB AUTO_INCREMENT=215 DEFAULT CHARSET=utf8 COMMENT='零钱包-货基年化收益率';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wallet_audit`
--

DROP TABLE IF EXISTS `wallet_audit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wallet_audit` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `wallet_account_id` int(11) unsigned NOT NULL,
  `local_transaction_id` int(12) DEFAULT NULL,
  `local_transaction_type` char(1) DEFAULT NULL,
  `local_transaction_amount` decimal(20,10) DEFAULT NULL,
  `local_transaction_time` timestamp NULL DEFAULT NULL,
  `remote_transaction_id` char(32) DEFAULT NULL,
  `remote_transaction_type` char(1) DEFAULT NULL,
  `remote_transaction_amount` decimal(20,10) DEFAULT NULL,
  `remote_transaction_time` timestamp NULL DEFAULT NULL,
  `audit_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `local_status` char(1) NOT NULL,
  `remote_status` char(1) NOT NULL,
  `is_modified` tinyint(1) DEFAULT '0',
  `is_confirmed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `index_local_transaction_id` (`local_transaction_id`),
  KEY `index_local_status` (`local_status`),
  KEY `index_remote_status` (`remote_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wallet_bankcard_binding`
--

DROP TABLE IF EXISTS `wallet_bankcard_binding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wallet_bankcard_binding` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `bankcard_id` int(11) unsigned NOT NULL,
  `provider_id` int(11) unsigned NOT NULL,
  `is_confirmed` tinyint(1) NOT NULL DEFAULT '0',
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wallet_bound_bankcard` (`bankcard_id`,`provider_id`)
) ENGINE=InnoDB AUTO_INCREMENT=292 DEFAULT CHARSET=utf8 COMMENT='零钱包-合作方银行卡绑定';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wallet_profile`
--

DROP TABLE IF EXISTS `wallet_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wallet_profile` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=79462 DEFAULT CHARSET=utf8 COMMENT='零钱包 - 用户信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wallet_profit`
--

DROP TABLE IF EXISTS `wallet_profit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wallet_profit` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `account_id` int(11) NOT NULL,
  `profit_amount` decimal(20,10) NOT NULL,
  `profit_date` date NOT NULL,
  `updated_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `wallet_profit_account_date` (`account_id`,`profit_date`)
) ENGINE=InnoDB AUTO_INCREMENT=762 DEFAULT CHARSET=utf8 COMMENT='零钱包-收益';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wallet_transaction`
--

DROP TABLE IF EXISTS `wallet_transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wallet_transaction` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `account_id` int(11) NOT NULL,
  `amount` decimal(20,10) NOT NULL,
  `type` char(1) NOT NULL DEFAULT '',
  `bankcard_id` int(11) NOT NULL,
  `status` char(1) NOT NULL DEFAULT '',
  `creation_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `transaction_id` char(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=762 DEFAULT CHARSET=utf8 COMMENT='零钱包-交易记录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wxplan_plan`
--

DROP TABLE IF EXISTS `wxplan_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wxplan_plan` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `gender` tinyint(4) NOT NULL DEFAULT '-1',
  `age` tinyint(4) NOT NULL DEFAULT '-1',
  `province_code` varchar(24) DEFAULT '-',
  `stock` tinyint(4) NOT NULL DEFAULT '-1',
  `rent` int(12) NOT NULL DEFAULT '-1',
  `mpayment` int(12) NOT NULL DEFAULT '-1',
  `insurance` int(12) NOT NULL DEFAULT '-1',
  `tour` int(12) NOT NULL DEFAULT '-1',
  `has_children` tinyint(4) NOT NULL DEFAULT '-1',
  `savings` int(12) NOT NULL DEFAULT '-1',
  `mincome` int(12) NOT NULL DEFAULT '-1',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8 COMMENT='用户小规划表单';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wxplan_report`
--

DROP TABLE IF EXISTS `wxplan_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wxplan_report` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(11) unsigned NOT NULL,
  `raise_quota` decimal(20,10) NOT NULL DEFAULT '0.0000000000',
  `tour_children` int(12) NOT NULL DEFAULT '0',
  `savings` int(12) NOT NULL DEFAULT '0',
  `erfund` int(12) NOT NULL DEFAULT '0',
  `erfund_factor` tinyint(4) NOT NULL DEFAULT '0',
  `disposable_income` decimal(20,10) NOT NULL DEFAULT '0.0000000000',
  `month_factor` int(12) NOT NULL DEFAULT '0',
  `mincome` int(12) NOT NULL DEFAULT '0',
  `pocket_money` int(12) NOT NULL DEFAULT '0',
  `mpayment` int(12) NOT NULL DEFAULT '0',
  `rent` int(12) NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `status` char(1) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_user` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COMMENT='小规划报告表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wxplan_salary`
--

DROP TABLE IF EXISTS `wxplan_salary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wxplan_salary` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `code` varchar(32) NOT NULL DEFAULT '-',
  `province` varchar(32) NOT NULL DEFAULT '-',
  `income` float(8,2) NOT NULL,
  `expenditure` float(8,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='各省市人均收支表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `wxplan_wage_level`
--

DROP TABLE IF EXISTS `wxplan_wage_level`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wxplan_wage_level` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `report_id` int(11) unsigned NOT NULL,
  `year_interval` tinyint(4) NOT NULL DEFAULT '0',
  `wage_level` float(8,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_report_year` (`report_id`,`year_interval`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COMMENT='N年后工资水平表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xyz_areas`
--

DROP TABLE IF EXISTS `xyz_areas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xyz_areas` (
  `id` int(12) NOT NULL,
  `code` varchar(120) NOT NULL,
  `sort` int(12) NOT NULL,
  `status` int(12) NOT NULL,
  `name` varchar(250) NOT NULL,
  `parent_id` int(12) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `parent_idx` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新一站保险地区信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xyz_insure`
--

DROP TABLE IF EXISTS `xyz_insure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xyz_insure` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `type` int(4) DEFAULT NULL,
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10002 DEFAULT CHARSET=utf8 COMMENT='新一站保险大类';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xyz_insure_plan`
--

DROP TABLE IF EXISTS `xyz_insure_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xyz_insure_plan` (
  `insure_id` int(12) NOT NULL,
  `plan_id` int(12) NOT NULL,
  PRIMARY KEY (`plan_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='大类和小类的映射';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xyz_order`
--

DROP TABLE IF EXISTS `xyz_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xyz_order` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `user_id` int(12) NOT NULL,
  `plan_id` int(12) NOT NULL,
  `order_id` bigint(25) NOT NULL DEFAULT '0',
  `order_status` tinyint(4) unsigned DEFAULT NULL,
  `underwrite_status` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `status` tinyint(4) unsigned DEFAULT NULL,
  `finality` tinyint(4) unsigned NOT NULL DEFAULT '0',
  `num` tinyint(4) NOT NULL DEFAULT '0',
  `price` int(12) NOT NULL,
  `total` int(12) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `begin_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `pay_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `refund_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_index` (`user_id`),
  KEY `xyz_order_index` (`order_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10110 DEFAULT CHARSET=utf8 COMMENT='儿童险订单';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xyz_order_payment`
--

DROP TABLE IF EXISTS `xyz_order_payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xyz_order_payment` (
  `payment_id` int(12) NOT NULL,
  `order_id` int(12) NOT NULL,
  `create_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='儿童险支付订单';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `xyz_plan`
--

DROP TABLE IF EXISTS `xyz_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `xyz_plan` (
  `id` int(12) NOT NULL,
  `type` int(4) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='新一站保险产品';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-05-19 15:05:30
