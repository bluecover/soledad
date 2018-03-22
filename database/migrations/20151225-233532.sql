-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE coupon ADD INDEX idx_user_id (user_id, creation_time);


COMMIT;

