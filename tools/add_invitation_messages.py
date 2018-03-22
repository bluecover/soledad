# coding: utf-8

"""
给所有注册用户增加邀请通知
"""

from libs.db.store import db
from core.models.group import invitation_reminder_group


def add_invitation_msg_to_all_users():
    sql = 'select id from account order by update_time desc;'
    rs = db.execute(sql)

    for id_, in rs:
        invitation_reminder_group.add_member(id_)


if __name__ == '__main__':
    add_invitation_msg_to_all_users()
