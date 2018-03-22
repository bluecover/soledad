-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE hoard_bankcard DROP INDEX idx_hoard_bankcard_bank;


COMMIT;

