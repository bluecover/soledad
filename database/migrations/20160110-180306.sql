-- Convert schema 'old-schema.sql' to 'new-schema.sql':;

BEGIN;

DROP TABLE activity;

DROP TABLE activity_award;

DROP TABLE activity_award_map;

DROP TABLE activity_content;

DROP TABLE activity_invite;

DROP TABLE activity_invite_code;

DROP TABLE activity_product;

DROP TABLE activity_realm;

DROP TABLE activity_task;

DROP TABLE activity_task_map;

DROP TABLE activity_task_user;

DROP TABLE activity_user;

DROP TABLE admin;

DROP TABLE alipay_payment;

DROP TABLE alipay_refund;

DROP TABLE bank;

DROP TABLE gift_coupon;

DROP TABLE gift_package;

DROP TABLE gift_package_illuminator;

DROP TABLE gift_package_monthly_landing;

DROP TABLE gift_package_monthly_publicize;

DROP TABLE gift_package_newcoming;

DROP TABLE gift_package_sns_landing;

DROP TABLE gift_package_sns_publicize;

DROP TABLE gift_package_user_calling;

DROP TABLE promotion_mid_autumn_2015;

DROP TABLE rice_pudding_ticket;


COMMIT;

