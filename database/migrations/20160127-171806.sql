-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

ALTER TABLE email DROP COLUMN to,
                  DROP COLUMN sender_type,
                  DROP COLUMN priority,
                  DROP COLUMN create_time,
                  ADD COLUMN receiver varchar(60) NOT NULL,
                  ADD COLUMN kind_id integer(11) unsigned NOT NULL,
                  ADD COLUMN creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00';


COMMIT;
