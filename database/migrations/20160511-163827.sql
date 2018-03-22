-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE site_bulletin ADD COLUMN expire_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00';


COMMIT;

