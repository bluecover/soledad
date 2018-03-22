# -*- coding: utf-8 -*-

from core.models.utils import pwd_hash, randbytes


def get_passwd_hash(password):
    salt = randbytes(4)
    passwd_hash = pwd_hash(salt, password)
    return salt, passwd_hash
