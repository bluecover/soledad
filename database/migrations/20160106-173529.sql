-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE coupon ADD COLUMN platforms char(32) NOT NULL DEFAULT '1,2,3' AFTER platform,
                   CHANGE COLUMN platform platform integer(2) NOT NULL DEFAULT 0;


COMMIT;

