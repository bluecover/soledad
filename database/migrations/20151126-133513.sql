-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE coupon ADD COLUMN platform integer(2) NOT NULL DEFAULT '0' AFTER status,
                   ADD COLUMN product_matcher_kind_id integer(8) NOT NULL DEFAULT '0' AFTER platform;


UPDATE coupon SET platform=0;
UPDATE coupon SET product_matcher_kind_id=100 WHERE kind_id NOT IN (1003,1004,1007);
UPDATE coupon SET product_matcher_kind_id=110 WHERE kind_id IN (1003,1004,1007);


COMMIT;

