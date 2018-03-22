-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE coupon_package_legacy_rebate (
  user_id integer(11) unsigned NOT NULL,
  package_id integer(11) unsigned NOT NULL,
  rebate_voucher_id char(32) NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (package_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='历史返现记录兼容礼包';

SET foreign_key_checks=1;

ALTER TABLE firewood_piling ADD COLUMN welfare_package_id integer(11) unsigned NOT NULL DEFAULT 0 AFTER amount,
                            CHANGE COLUMN gather_ghat_id gather_ghat_id integer(11) unsigned NOT NULL DEFAULT 0,
                            CHANGE COLUMN gather_voucher_id gather_voucher_id char(32) NOT NULL DEFAULT '';


COMMIT;

