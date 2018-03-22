-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE coupon_package_redeem_celebration (
  package_id integer(11) unsigned NOT NULL,
  user_id integer(11) unsigned NOT NULL,
  provider_id integer(4) NOT NULL,
  order_id char(32) NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (package_id),
  UNIQUE idx_provider_order (provider_id, order_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='任意产品订单到期奖励礼包';

SET foreign_key_checks=1;


COMMIT;

