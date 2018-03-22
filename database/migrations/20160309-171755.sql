-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE coupon_package_xm (
  id integer(11) unsigned NOT NULL auto_increment,
  order_id integer(11) unsigned NOT NULL,
  package_id integer(11) unsigned NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARACTER SET utf8 comment='新结算礼包';

SET foreign_key_checks=1;


COMMIT;

