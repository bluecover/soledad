-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE hoard_zhiwang_order ADD INDEX index_create_time (creation_time),
                                ADD INDEX index_status (status);


COMMIT;

