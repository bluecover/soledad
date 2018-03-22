-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE hoarder_product DROP INDEX vendor_product, ADD UNIQUE KEY `vendor_product_kind` (`vendor_id`,`remote_id`,`kind`);


COMMIT;

