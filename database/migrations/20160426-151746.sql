-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE hoarder_asset DROP COLUMN hold_amount;
ALTER TABLE hoarder_asset DROP COLUMN uncollected_amount;

COMMIT;
