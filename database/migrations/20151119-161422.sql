-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE wallet_account ADD COLUMN updated_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00';


COMMIT;

