-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

UPDATE coupon SET expire_time=DATE_SUB(expire_time, INTERVAL 1 second);

COMMIT;

