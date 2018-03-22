-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE hoarder_bankcard_binding (
  id integer(11) unsigned NOT NULL auto_increment,
  user_id integer(11) unsigned NOT NULL,
  bankcard_id integer(11) unsigned NOT NULL,
  vendor_id integer(11) unsigned NOT NULL,
  is_confirmed tinyint(1) NOT NULL DEFAULT 0,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARACTER SET utf8 comment='hoarder银行卡绑定';

SET foreign_key_checks=1;


COMMIT;

