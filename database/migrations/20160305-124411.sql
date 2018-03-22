-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE hoard_xm_asset MODIFY COLUMN product_id VARCHAR(32) NOT NULL;
ALTER TABLE hoard_xm_product MODIFY COLUMN product_id VARCHAR(32) NOT NULL;
ALTER TABLE hoard_xm_order MODIFY COLUMN product_id VARCHAR(32) NOT NULL;


COMMIT;

