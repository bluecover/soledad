-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE hoard_zhiwang_product ADD INDEX idx_date (start_sell_date, end_sell_date, creation_time);


COMMIT;

