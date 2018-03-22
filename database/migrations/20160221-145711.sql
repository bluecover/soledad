-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE pusher_device_binding (
  id integer(11) unsigned NOT NULL auto_increment,
  user_id integer(11) unsigned NOT NULL,
  device_id varchar(32) NOT NULL,
  status char(1) NOT NULL,
  platform tinyint(2) NOT NULL,
  app_version char(32) NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  update_time timestamp on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX user_index (user_id),
  PRIMARY KEY (id),
  UNIQUE device_id (device_id)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARACTER SET utf8 comment='极光推送设备';

CREATE TABLE pusher_group_record (
  id integer(11) unsigned NOT NULL auto_increment,
  notification_kind_id integer(8) NOT NULL,
  subdivision_kind_id integer(8) unsigned NULL DEFAULT NULL,
  is_pushed tinyint(1) NOT NULL,
  jmsg_id char(32) NOT NULL DEFAULT '',
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  push_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARACTER SET utf8 comment='通知推送组播记录';

CREATE TABLE pusher_universe_record (
  id integer(11) unsigned NOT NULL auto_increment,
  bulletin_id integer(11) unsigned NOT NULL,
  is_pushed tinyint(1) NOT NULL,
  jmsg_id char(32) NOT NULL DEFAULT '',
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  push_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  INDEX bulletin_index (bulletin_id),
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARACTER SET utf8 comment='通知推送广播记录';

CREATE TABLE pusher_user_record (
  id integer(11) unsigned NOT NULL auto_increment,
  user_id integer(11) unsigned NOT NULL,
  device_id varchar(32) NOT NULL,
  notification_id integer(11) unsigned NOT NULL,
  status char(1) NOT NULL,
  jmsg_id char(32) NOT NULL DEFAULT '',
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  push_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  received_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  clicked_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  INDEX user_index (user_id),
  INDEX jmsg_index (jmsg_id),
  PRIMARY KEY (id),
  UNIQUE device_notification (device_id, notification_id)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARACTER SET utf8 comment='通知推送单播记录';

CREATE TABLE site_bulletin (
  id integer(11) unsigned NOT NULL auto_increment,
  title_content_sha1 varchar(40) NOT NULL,
  platforms char(32) NOT NULL,
  cast_kind char(1) NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id),
  UNIQUE idx_tc_sha1 (title_content_sha1)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARACTER SET utf8 comment='APP运营布告';

CREATE TABLE user_tag (
  id integer(11) unsigned NOT NULL auto_increment,
  user_id integer(11) unsigned NOT NULL,
  tag varchar(32) NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  INDEX tag_index (tag),
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARACTER SET utf8 comment='极光推送标签';

SET foreign_key_checks=1;


COMMIT;

