-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE advert_record (
  id integer(12) NOT NULL auto_increment,
  user_id integer(11) unsigned NOT NULL,
  kind_id integer(11) unsigned NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id),
  UNIQUE user_kind (kind_id, user_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='好规划广告点击记录';

SET foreign_key_checks=1;


COMMIT;

