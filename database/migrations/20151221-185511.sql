-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE notification (
  id integer(11) unsigned NOT NULL auto_increment,
  user_id integer(11) unsigned NOT NULL,
  kind_id integer(8) NOT NULL,
  is_read tinyint(1) NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  read_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARACTER SET utf8 comment='消息通知';

SET foreign_key_checks=1;


COMMIT;

