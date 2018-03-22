-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE insurance_plan (
  id integer(12) NOT NULL auto_increment,
  user_id integer(12) NOT NULL,
  create_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  update_time timestamp on update CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user (user_id),
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='用户保险规划表单';

SET foreign_key_checks=1;


COMMIT;

