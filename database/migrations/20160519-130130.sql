-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE hoarder_product ADD COLUMN kind char(1) NOT NULL;


COMMIT;

