-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE promotion_christmas_2015 (
  id integer(11) unsigned NOT NULL auto_increment,
  mobile_phone varchar(11) NOT NULL DEFAULT '',
  rank integer(11) unsigned NOT NULL,
  is_awarded tinyint(1) NOT NULL,
  updated_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  created_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id),
  UNIQUE mobile_phone (mobile_phone)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='2015 圣诞节烤蛋糕小游戏';

SET foreign_key_checks=1;


COMMIT;

