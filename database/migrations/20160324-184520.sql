-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE coupon_package_xm ADD UNIQUE order_id (order_id);


COMMIT;

