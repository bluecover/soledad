-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE hoarder_order_gift_usage_record (
  id integer(12) NOT NULL auto_increment,
  product_id integer(11) unsigned NOT NULL,
  order_id integer(11) unsigned NOT NULL,
  effective_amount decimal(20, 10) NOT NULL,
  gift_type char(1) NOT NULL,
  status char(1) NOT NULL,
  effective_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  end_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id),
  UNIQUE product_order (product_id, order_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='产品使用优惠记录';

SET foreign_key_checks=1;


COMMIT;

