-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE user_channel (
  id integer(11) unsigned NOT NULL auto_increment,
  name varchar(30) NOT NULL DEFAULT '',
  tag varchar(21) NOT NULL DEFAULT '',
  is_enabled tinyint(1) NOT NULL,
  creation_time timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX tag (tag),
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='用户注册的商务渠道';

CREATE TABLE user_channel_register (
  user_id integer(11) unsigned NOT NULL auto_increment,
  channel_id integer(11) unsigned NOT NULL,
  INDEX channel_id (channel_id),
  PRIMARY KEY (user_id),
  UNIQUE user_id (user_id, channel_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='用户和商务渠道的对应关系';

SET foreign_key_checks=1;


COMMIT;

