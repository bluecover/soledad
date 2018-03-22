# coding: utf-8

import re
import sys
import subprocess

from jupiter.app import create_app
from libs.utils.log import bcolors
from core.models.user.account import Account
from core.models.hoard.zhiwang import ZhiwangAccount
from core.models.hoard.zhiwang.errors import (
    MismatchUserError, RepeatlyRegisterError)
from core.models.hoard.zhiwang.transaction import register_zhiwang_account
from .add_zhiwang import __file__ as _add_zhiwang_file


EMAIL = u'zw@guihua.com'
RE_ZHIWANG_CODE = re.compile(r'^ZHIWANG_TOKEN = .+$', re.MULTILINE)
ADD_ZHIWANG_FILE = _add_zhiwang_file.replace('.pyc', '.py')
COMMIT_MSG = '[AUTO] [CI SKIP] UPDATE ZHIWANG CODE'


def main():
    user = Account.get_by_alias(EMAIL)
    ZhiwangAccount.unbind(user.id_)

    try:
        register_zhiwang_account(user.id_)
        zhiwang_account = ZhiwangAccount.get_by_local(user.id_)
    except (MismatchUserError, RepeatlyRegisterError) as e:
        bcolors.fail(e.args[0], key='zhiwang_code')
        return

    bcolors.run(
        'The new zhiwang code is %s' % zhiwang_account.zhiwang_id,
        key='zhiwang_code')

    with open(ADD_ZHIWANG_FILE, 'r') as f:
        source = RE_ZHIWANG_CODE.sub(
            "ZHIWANG_TOKEN = u'%s'" % zhiwang_account.zhiwang_id.encode('ascii'), f.read())
    with open(ADD_ZHIWANG_FILE, 'w') as f:
        f.write(source)

    bcolors.run(
        '%s is changed. PLEASE COMMIT IT AND OPEN A MERGE REQUEST.' % ADD_ZHIWANG_FILE,
        key='zhiwang_code')

    if '--commit' in sys.argv:
        subprocess.check_call(['git', 'commit', '-m', COMMIT_MSG, '--', ADD_ZHIWANG_FILE])


if __name__ == '__main__':
    with create_app().app_context():
        main()
