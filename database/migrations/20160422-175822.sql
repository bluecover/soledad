-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE hoarder_order ADD COLUMN direction CHAR(1) NOT NULL DEFAULT 'S';
ALTER TABLE hoarder_order MODIFY COLUMN remote_status CHAR(2) NOT NULL DEFAULT '00';

COMMIT;
