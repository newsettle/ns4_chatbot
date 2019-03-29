-- 值班表
DROP TABLE IF EXISTS cb_duty;
CREATE TABLE IF NOT EXISTS cb_duty
(
	`id` 		INT 			NOT NULL	AUTO_INCREMENT,
	duty_date 	DATE 			comment '值班日期',
	duration 	VARCHAR(100) 	comment '上午还是下午AM|PM两个值',
	duty_person	VARCHAR(100)	comment '值班人',
	`group`		VARCHAR(100)	comment '所属组：支付核心组	测试组,运维组,DBA组,账务-资金托管,运营组,付钱拉,现金罗盘',
    PRIMARY KEY ( `id` )
)ENGINE=InnoDB
DEFAULT CHARSET=utf8
comment='值班表';

-- 系统群组关系表
DROP TABLE IF EXISTS `biz_system_tree`;
CREATE TABLE `biz_system_tree` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `node_code` varchar(32) DEFAULT NULL COMMENT '系统编码',
  `node_name` varchar(50) DEFAULT NULL COMMENT '系统名称',
  `ower_name` varchar(20) DEFAULT NULL COMMENT '负责人',
  `qq_group` varchar(100) DEFAULT NULL COMMENT 'QQ群',
  `wechat_group` varchar(100) DEFAULT NULL COMMENT '微信群',
  `ower_email` varchar(30) DEFAULT NULL COMMENT '邮箱',
  `ower_telphone` varchar(20) DEFAULT NULL COMMENT '电话',
  `update_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日期(YYYY-MM-DD HH24:Mi:ss)',
  `remark` varchar(1024) DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COMMENT='系统_小组映射表';

-- ----------------------------
-- Records of biz_system_tree
-- ----------------------------

INSERT INTO `biz_system_tree` VALUES ('1', 'rootsystem', '结算系统', '张三', '自动化组', '自动化组', '', null, '2018-11-15 10:54:54', null);
INSERT INTO `biz_system_tree` VALUES ('2', 'NEWSETTLEMENT', '新结算', '张三', '自动化组', '自动化组', '', null, '2018-11-15 10:54:53', null);
INSERT INTO `biz_system_tree` VALUES ('3', 'CASHCOMPASS', '现金罗盘', '张三', '现金罗盘-新结算', '自动化组', '', null, '2018-11-15 10:59:18', null);
