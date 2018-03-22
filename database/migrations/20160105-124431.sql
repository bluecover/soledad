-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE hoard_zhiwang_loan (
  id integer(11) unsigned NOT NULL auto_increment,
  loans_digest_id integer(11) unsigned NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  INDEX ‘index_loans_digest_id’ (loans_digest_id),
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='指旺资产借贷人信息表';

CREATE TABLE hoard_zhiwang_loans_digest (
  id integer(11) unsigned NOT NULL auto_increment,
  asset_id integer(11) unsigned NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (id),
  UNIQUE idx_asset_id (asset_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='指旺资产借贷信息摘要';

SET foreign_key_checks=1;


COMMIT;

