-- MySQL dump 10.13  Distrib 5.5.40, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: haoguihua
-- ------------------------------------------------------
-- Server version	5.5.40-0+wheezy1-log

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
-- Table structure for table `bank`
--

DROP TABLE IF EXISTS `bank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bank` (
  `province_id` int(12) NOT NULL,
  `bank_id` int(12) NOT NULL,
  `cnap_id` varchar(20) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `child_id` int(12) NOT NULL,
  `child_name` varchar(20) NOT NULL,
  `bank_name` varchar(80) NOT NULL,
  `bank_address` varchar(200) NOT NULL,
  `child_location_id` int(12) NOT NULL DEFAULT '0',
  KEY `search_bank` (`bank_id`,`province_id`,`child_location_id`),
  KEY `search_bank_location` (`bank_id`,`child_location_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='银行信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bank`
--
-- WHERE:  1 limit 100

LOCK TABLES `bank` WRITE;
/*!40000 ALTER TABLE `bank` DISABLE KEYS */;
INSERT INTO `bank` VALUES (340000,3,'103361008002','0551--3427325',3610,'合肥市','中国农业银行股份有限公司安徽省分行营业部清算中心','合肥市青年路11号',340100),(340000,3,'103361008117','0551-4240465',3610,'合肥市','中国农业银行合肥新站综合试验区支行','安徽省合肥市站西路2号宝文国际花园',340100),(340000,3,'103361008205','2643586',3610,'合肥市','中国农业银行合肥市长江路支行','合肥市长江路312号',340100),(340000,3,'103361008213','2887249',3610,'合肥市','中国农业银行合肥市钟楼支行','合肥市芜湖路287号',340100),(340000,3,'103361008221','0551-2886454',3610,'合肥市','中国农业银行合肥市芜湖东路分理处','安徽省合肥市芜湖路27号',340100),(340000,3,'103361008230','0551-3653084',3610,'合肥市','中国农业银行合肥市黄山路分理处','合肥市黄山路373号',340100),(340000,3,'103361008248','0551-2816642',3610,'合肥市','中国农业银行合肥市琥珀分理处','安徽省合肥市琥珀山庄南村商业网点55幢101',340100),(340000,3,'103361008256','2642361',3610,'合肥市','中国农业银行合肥市徽州路支行','合肥市徽州路66号',340100),(340000,3,'103361008264','0551-5112132',3610,'合肥市','中国农业银行合肥学府花园分理处','安徽省合肥市西园新村西园路2－108号',340100),(340000,3,'103361008272','0551-5127304',3610,'合肥市','中国农业银行合肥市蜀山新村分理处','安徽省合肥市长江西路242号',340100),(340000,3,'103361008289','0551-2641422',3610,'合肥市','中国农业银行濉溪路分理处','安徽省合肥市长江中路136号',340100),(340000,3,'103361008297','0551-3361004',3610,'合肥市','中国农业银行合肥市义城分理处','安徽省合肥市包河区义城镇汪潦路52号',340100),(340000,3,'103361008416','0551-2828932',3610,'合肥市','中国农业银行合肥安庆路支行','安徽省合肥市安庆路264号',340100),(340000,3,'103361008424','0551-5541840',3610,'合肥市','中国农业银行合肥市明珠支行阜阳北路分理处','安徽省合肥市阜阳路123号',340100),(340000,3,'103361008432','3415654',3610,'合肥市','中国农业银行合肥市包河支行','合肥市合巢路342号',340100),(340000,3,'103361008449','2872664',3610,'合肥市','中国农业银行合肥市芜湖路支行','合肥市芜湖路361号',340100),(340000,3,'103361008457','0551-3421272',3610,'合肥市','中国农业银行合肥市望江东路分理处','安徽省合肥市望江东路115号',340100),(340000,3,'103361008607','5561205',3610,'合肥市','中国农业银行合肥市城西支行','合肥市长江西路563号',340100),(340000,3,'103361008615','0551-5380661',3610,'合肥市','中国农业银行合肥市蜀山分理处','长江西路1004号',340100),(340000,3,'103361008623','5311385',3610,'合肥市','中国农业银行合肥市高新技术开发区支行','合肥市高新区创业大道',340100),(340000,3,'103361008640','0551-5106387',3610,'合肥市','中国农业银行合肥市新政务区支行','合肥市合作北路188号',340100),(340000,3,'103361008658','0551-5563482',3610,'合肥市','中国农业银行合肥市安居苑分理处','安徽省合肥市青阳路安居苑东路口商网101号',340100),(340000,3,'103361008703','0551-5671435',3610,'合肥市','中国农业银行股份有限公司合肥史河路支行','安徽省合肥市蜀山区史河路38号',340100),(340000,3,'103361008800','4224607',3610,'合肥市','中国农业银行合肥市明珠支行','合肥市凤阳路468号',340100),(340000,3,'103361008818','0551-4293124',3610,'合肥市','中国农业银行合肥市胜利路分理处','安徽省合肥市胜利路18号',340100),(340000,3,'103361008826','0551-4228976',3610,'合肥市','中国农业银行合肥市瑶海分理处','安徽省合肥市琅琊山路58号',340100),(340000,3,'103361008842','0551-4210424',3610,'合肥市','中国农业银行合肥市明珠支行三里街分理处','安徽省合肥市长江东路918号',340100),(340000,3,'103361008906','0551-3645770',3610,'合肥市','中国农业银行股份有限公司安徽省分行营业部','安徽省合肥市曙光路12号2幢',340100),(340000,3,'103361018005','2675233',3610,'合肥市','中国农业银行合肥市绿都支行','合肥市绿都支行',340100),(340000,3,'103361018101','3661293',3610,'合肥市','中国农业银行合肥市金寨路支行','合肥市金寨路209号',340100),(340000,3,'103361018208','0551-2905028',3610,'合肥市','中国农业银行合肥市金穗支行','合肥市屯溪路193号',340100),(340000,3,'103361018304','4659904',3610,'合肥市','中国农业银行合肥市东陈岗支行','合肥市美菱大道338号',340100),(340000,3,'103361018407','0551-4681246',3610,'合肥市','中国农业银行合肥市屯溪路支行','安徽省合肥市屯溪路168号',340100),(340000,3,'103361018503','2645841',3610,'合肥市','中国农业银行合肥市三牌楼支行','合肥市长江路53号',340100),(340000,3,'103361018600','2655815－8020',3610,'合肥市','中国农业银行合肥市逍遥津支行','合肥市逍遥津路1号',340100),(340000,3,'103361018618','0551-2634717',3610,'合肥市','中国农业银行绩溪路分理处','安徽省合肥市金寨路209号',340100),(340000,3,'103361018706','2223395',3610,'合肥市','中国农业银行合肥市金城支行','合肥市长江路448号',340100),(340000,3,'103361018909','3813313',3610,'合肥市','中国农业银行合肥市经济开发区支行','合肥市经济技术开发区芙蓉路2621号东海花园22幢101室',340100),(340000,3,'103361028003','7711978',3610,'合肥市','中国农业银行肥东县支行营业部','肥东店埠龙泉中路46号',340100),(340000,3,'103361028011','0551-7721903',3610,'合肥市','中国农业银行肥东县店埠营业所','安徽省肥东县店埠镇新街28号',340100),(340000,3,'103361028020','7672999',3610,'合肥市','中国农业银行合肥市龙岗支行','合肥市长江东路89号',340100),(340000,3,'103361028046','0551-7711581',3610,'合肥市','中国农业银行肥东县城关分理处','安徽省肥东县店埠镇龙泉西路',340100),(340000,3,'103361028054','0551-7361203',3610,'合肥市','中国农业银行肥东县撮镇营业所','安徽省肥东县撮镇南大街117号',340100),(340000,3,'103361028062','0551-7286205',3610,'合肥市','中国农业银行肥东县梁园营业所','安徽省肥东县梁园镇太平南路',340100),(340000,3,'103361028079','0551-7451258',3610,'合肥市','中国农业银行肥东县石塘营业所','安徽省肥东县石塘镇金桥大街',340100),(340000,3,'103361028087','0551-7396271',3610,'合肥市','中国农业银行肥东县长临河营业所','安徽省肥东县长临河镇新街33号',340100),(340000,3,'103361028095','0551-7331268',3610,'合肥市','中国农业银行肥东县桥头集营业所','安徽省肥东县桥头集镇龙泉路',340100),(340000,3,'103361028118','0551-7686598',3610,'合肥市','中国农业银行肥东县恒通分理处','安徽省合肥市长江东路195号',340100),(340000,3,'103361028302','8841410',3610,'合肥市','中国农业银行肥西县支行营业部','合肥市肥西县',340100),(340000,3,'103361028319','0551-8501029',3610,'合肥市','中国农业银行肥西县支行小庙营业所','安徽省肥西县小庙镇庙塘路99号',340100),(340000,3,'103361028327','0551-8751326',3610,'合肥市','中国农业银行肥西县支行三河分理处','安徽省肥西县三河镇北街58号',340100),(340000,3,'103361028335','0551-8841219',3610,'合肥市','中国农业银行肥西县支行巢湖路分理处','安徽省肥西县上派镇巢湖中路',340100),(340000,3,'103361028343','0551-8991422',3610,'合肥市','中国农业银行桃花工业园区支行','安徽省合肥市经济技术开发区石门路2号',340100),(340000,3,'103361028351','0551-8841912',3610,'合肥市','中国农业银行肥西县支行上派营业所','安徽省肥西县上派镇三河路12号',340100),(340000,3,'103361028360','0551-8201483',3610,'合肥市','中国农业银行肥西县支行山南营业所','安徽省肥西县山南镇杨桃路181号',340100),(340000,3,'103361028386','0551-8361316',3610,'合肥市','中国农业银行肥西县支行官亭营业所','安徽省肥西县官亭镇中街78号',340100),(340000,3,'103361028394','0551-8401981',3610,'合肥市','中国农业银行肥西县支行花岗营业所','安徽省肥西县花岗镇花新路3号',340100),(340000,3,'103361028409','0551-3831196',3610,'合肥市','中国农业银行肥西县支行翡翠路分理处','安徽省合肥市经济技术开发区翡翠路',340100),(340000,3,'103361028417','0551-8583958',3610,'合肥市','中国农业银行肥西县支行紫蓬山分理处','安徽省合肥市紫蓬山文达学院北门',340100),(340000,3,'103361028425','0551-8841126',3610,'合肥市','中国农业银行肥西县支行包公路分理处','安徽省肥西县包公路',340100),(340000,3,'103361028601','6671304',3610,'合肥市','中国农业银行长丰县支行营业部','长丰县水湖镇长丰路',340100),(340000,3,'103361028636','0551-6674237',3610,'合肥市','中国农业银行长丰县支行长寿路分理处','安徽省长丰县水湖镇长寿路',340100),(340000,3,'103361028652','0551-5541780',3610,'合肥市','中国农业银行合肥市绿都花园分理处','安徽省合肥市荣事达大道（绿都花园21号楼）',340100),(340000,3,'103361028669','0551-6471074',3610,'合肥市','中国农业银行长丰县支行下塘营业所','安徽省长丰县下塘镇',340100),(340000,3,'103361028677','0551-6374033',3610,'合肥市','中国农业银行长丰县支行双墩营业所','安徽省长丰县双墩镇',340100),(340000,3,'103361028685','0551-6841014',3610,'合肥市','中国农业银行长丰县支行朱巷营业所','安徽省长丰县朱巷镇',340100),(340000,3,'103361028693','0551-6511011',3610,'合肥市','中国农业银行长丰县支行杨庙营业所','安徽省长丰县杨庙镇',340100),(340000,3,'103361028708','0551-6709019',3610,'合肥市','中国农业银行长丰县支行吴山营业所','安徽省长丰县吴山镇',340100),(340000,3,'103361028716','0551-6671056',3610,'合肥市','中国农业银行长丰县支行岗集营业所','安徽省长丰县岗集镇',340100),(340000,3,'103361028724','0551-6396111',3610,'合肥市','中国农业银行长丰县支行双凤分理处','安徽省合肥市双凤开发区双凤大道',340100),(340000,3,'103361099995','2842774',3610,'合肥市','中国农业银行安徽省分行（不对外办业务）','合肥市长江中路448号',340100),(340000,6,'308361030017','0551-2810594',3610,'合肥市','招商银行股份有限公司合肥分行','合肥市阜南路169号招行大厦',340100),(340000,6,'308361030025','0551-2844337',3610,'合肥市','招商银行股份有限公司合肥分行营业部','合肥市阜南路169号招行大厦',340100),(340000,6,'308361030033','0551-4682916',3610,'合肥市','招商银行合肥大钟楼支行','合肥市屯溪路251号世纪云顶大厦1楼',340100),(340000,6,'308361030041','0551-2621491',3610,'合肥市','招商银行合肥四牌楼支行','合肥市美菱大道507号',340100),(340000,6,'308361030050','0551－5584803',3610,'合肥市','招商银行合肥五里墩支行','合肥市长江西路365号',340100),(340000,6,'308361030068','0551－4656773',3610,'合肥市','招商银行合肥马鞍山路支行','合肥市马鞍山路100号',340100),(340000,6,'308361030076','0551-3662125',3610,'合肥市','招商银行合肥南七支行','合肥市金寨路2号金江大厦',340100),(340000,6,'308361030084','0551-3633297',3610,'合肥市','招商银行股份有限公司合肥金屯支行','合肥市屯溪路258号',340100),(340000,6,'308361030092','0551-2609452',3610,'合肥市','招商银行股份有限公司合肥长江路支行','安徽省合肥市长江中路7号',340100),(340000,6,'308361030105','0551-4214557',3610,'合肥市','招商银行股份有限公司合肥新站支行','合肥市新站区胜利路与站前路交口光大国际城1-2层',340100),(340000,6,'308361030113','0551-3613330',3610,'合肥市','招商银行合肥黄山路支行','安徽省合肥市黄山路9号安徽电网调度大楼裙楼一楼',340100),(340000,6,'308361030121','0551-5601403',3610,'合肥市','招商银行股份有限公司合肥亳州路支行','合肥市亳州路33号天庆大厦1楼',340100),(340000,6,'308361030130','3629921',3610,'合肥市','招商银行股份有限公司合肥肥西路支行','黄山路330号',340100),(340000,6,'308361030148','05512810594',3610,'合肥市','招商银行股份有限公司合肥经开区支行','合肥市繁华路南繁华世家B区',340100),(340000,6,'308361030156','2810594',3610,'合肥市','招商银行股份有限公司合肥卫岗支行','合肥市徽州大道与太湖路交叉口恒生阳光城',340100),(340000,6,'308361030164','0551-2812331',3610,'合肥市','招商银行股份有限公司合肥分行票据中心','合肥市长江中路436号金城大厦裙楼',340100),(340000,16,'309361001010','0551-2666231',3610,'合肥市','兴业银行股份有限公司合肥分行专业处理中心','合肥市阜阳路99号',340100),(340000,16,'309361009014','0551-2669235、2666317',3610,'合肥市','兴业银行股份有限公司合肥分行营业部','合肥市阜阳路99号',340100),(340000,16,'309361009022','2853650',3610,'合肥市','兴业银行股份有限公司合肥寿春路支行','合肥市寿春路365-1号徽商国际大厦一楼',340100),(340000,16,'309361009039','0551-2881255',3610,'合肥市','兴业银行股份有限公司合肥徽州路支行','合肥市徽州大道418号',340100),(340000,16,'309361009047','0551-2669239',3610,'合肥市','兴业银行股份有限公司合肥长江中路支行','合肥市长江中路319号',340100),(340000,16,'309361009055','0551-4687596',3610,'合肥市','兴业银行股份有限公司合肥马鞍山路支行','合肥市马鞍山路77号拓佳新天地广场',340100),(340000,16,'309361009063','0551-2153506',3610,'合肥市','兴业银行合肥黄山路支行','合肥市黄山路385号外运大厦',340100),(340000,16,'309361009071','0551-2359267',3610,'合肥市','兴业银行股份有限公司合肥政务区支行','安徽省合肥市政务区祁门路1777号',340100),(340000,16,'309361009080','0551-2650888-600806',3610,'合肥市','兴业银行股份有限公司合肥胜利路支行','合肥市胜利路88号',340100),(340000,4,'105361000019','0551-2872994\\\\287337',3610,'合肥市','中国建设银行安徽分行','合肥市美菱大道373号',340100),(340000,4,'105361044013','0551-4224973',3610,'合肥市','中国建设银行合肥市城东支行营业部','合肥新站开发区万事达广场1号楼',340100),(340000,4,'105361044021','0551-4294809',3610,'合肥市','中国建设银行股份有限公司合肥马鞍山路支行','安徽省合肥市马鞍山南路598号文景雅居1号楼',340100),(340000,4,'105361044030','0551-4225344',3610,'合肥市','中国建设银行合肥市长江东路支行','合肥市长江东路692号',340100);
/*!40000 ALTER TABLE `bank` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-12-02 11:38:14
