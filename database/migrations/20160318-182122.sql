-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE hoard_xm_asset ADD COLUMN remote_status char(2) NOT NULL DEFAULT '00';

ALTER TABLE hoard_xm_order ADD COLUMN remote_status char(2) NOT NULL DEFAULT '00';


COMMIT;

