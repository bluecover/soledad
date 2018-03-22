-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE hoard_zhiwang_product ADD COLUMN start_sell_date date NOT NULL DEFAULT '0000-00-00',
                                  ADD COLUMN end_sell_date date NOT NULL DEFAULT '0000-00-00';


COMMIT;

