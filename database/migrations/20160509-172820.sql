-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE app_banner (
  id integer(11) unsigned NOT NULL auto_increment,
  name varchar(64) NOT NULL DEFAULT '',
  status char(1) NOT NULL,
  image_url text NOT NULL,
  link_url text NOT NULL,
  sequence integer(11) NOT NULL DEFAULT 0,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARACTER SET utf8 comment='App首页Banner';

SET foreign_key_checks=1;


COMMIT;

