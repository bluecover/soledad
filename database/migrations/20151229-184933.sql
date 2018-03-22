-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE coupon_package_redeem_code (
  id integer(11) unsigned NOT NULL auto_increment,
  redeem_code_usage_id integer(11) unsigned NOT NULL,
  package_id integer(11) unsigned NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='兑换码礼包';

CREATE TABLE redeem_code (
  id integer(11) unsigned NOT NULL auto_increment,
  code varchar(10) NOT NULL,
  activity_id integer(11) unsigned NOT NULL,
  source char(1) NOT NULL,
  max_usage_limit_per_code integer(10) NOT NULL,
  kind integer(10) NOT NULL,
  status char(1) NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  effective_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  expire_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id),
  UNIQUE code (code)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='兑换码表';

CREATE TABLE redeem_code_usage (
  id integer(11) unsigned NOT NULL auto_increment,
  code_id integer(11) unsigned NOT NULL,
  user_id integer(11) unsigned NOT NULL,
  activity_id integer(11) unsigned NOT NULL,
  consumed_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id),
  UNIQUE code_id (code_id, user_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='兑换码使用表';

SET foreign_key_checks=1;


COMMIT;

