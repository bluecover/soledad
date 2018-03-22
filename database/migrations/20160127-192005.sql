-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE hoard_placebo_order (
  id integer(11) unsigned NOT NULL auto_increment,
  user_id integer(10) unsigned NOT NULL,
  product_id integer(10) unsigned NOT NULL,
  bankcard_id integer(10) unsigned NOT NULL,
  amount decimal(20, 10) unsigned NOT NULL,
  annual_rate_hike decimal(20, 10) unsigned NOT NULL,
  status integer(10) unsigned NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 comment='攒钱助手体验金-订单';

CREATE TABLE hoard_placebo_product (
  id integer(11) unsigned NOT NULL auto_increment,
  strategy_id integer(10) unsigned NOT NULL,
  min_amount decimal(20, 10) NOT NULL,
  max_amount decimal(20, 10) NOT NULL,
  start_sell_date date NOT NULL,
  end_sell_date date NOT NULL,
  frozen_days integer(10) unsigned NOT NULL,
  annual_rate decimal(20, 10) NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 comment='攒钱助手体验金-产品';

CREATE TABLE promotion_spring_2016 (
  id integer(11) unsigned NOT NULL auto_increment,
  mobile_phone varchar(11) NOT NULL DEFAULT '',
  status char(1) NOT NULL DEFAULT '',
  order_id integer(11) unsigned NULL DEFAULT NULL,
  user_id integer(11) unsigned NULL DEFAULT NULL,
  reserved_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  obtained_time timestamp NULL DEFAULT '0000-00-00 00:00:00',
  upgraded_time timestamp NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id),
  UNIQUE mobile_phone (mobile_phone),
  UNIQUE user_id (user_id),
  UNIQUE order_id (order_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8mb4 comment='2016 春节活动: 攒钱送体验金';

SET foreign_key_checks=1;


COMMIT;

