-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE promotion_christmas_2015 ADD COLUMN awarded_package_id integer(11) unsigned NOT NULL DEFAULT 0;


COMMIT;

