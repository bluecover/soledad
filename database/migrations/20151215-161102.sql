-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

SET foreign_key_checks=0;

CREATE TABLE coupon_package_investment_invitation_reward (
  invitation_id integer(11) unsigned NOT NULL,
  package_id integer(11) unsigned NOT NULL,
  creation_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (package_id),
  UNIQUE invitation_id (invitation_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='邀请新人奖励记录表';

CREATE TABLE invitation (
  id integer(11) unsigned NOT NULL auto_increment,
  invitee_id integer(11) unsigned NOT NULL,
  inviter_id integer(11) unsigned NOT NULL,
  kind integer(11) unsigned NOT NULL,
  status char(1) NOT NULL,
  expire_time timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  INDEX index_inviter_id (inviter_id),
  PRIMARY KEY (id),
  UNIQUE invitee_id (invitee_id)
) ENGINE=InnoDB DEFAULT CHARACTER SET utf8 comment='邀请新人活动记录表';

SET foreign_key_checks=1;


COMMIT;

