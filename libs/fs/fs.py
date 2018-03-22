import urlparse
import datetime

import qiniu
from flask import url_for
from werkzeug.security import gen_salt
from envcfg.json.solar import DEBUG
try:
    from envcfg.json.solar import QINIU_AK, QINIU_SK
except ImportError:
    QINIU_AK = QINIU_SK = None

from libs.cache import mc


class QiniuFS(object):
    def __init__(self, bucket_name, base_url):
        self.bucket_name = bucket_name
        self.base_url = base_url

    @classmethod
    def make_auth(cls):
        return qiniu.Auth(QINIU_AK.encode('ascii'), QINIU_SK.encode('ascii'))

    def upload(self, data, mime_type, key=None):
        auth = self.make_auth()
        token = auth.upload_token(self.bucket_name)
        key = key or gen_salt(16)
        r, info = qiniu.put_data(token, key, data, mime_type=mime_type)
        if r is None:
            raise UploadError(r, info)
        return r, info

    def get_url(self, key, is_private=False,
                expires=datetime.timedelta(hours=1)):
        url = urlparse.urljoin(self.base_url, '/' + key.rstrip('/'))
        expires = int(expires.total_seconds())
        if is_private:
            auth = self.make_auth()
            url = auth.private_download_url(url, expires=expires)
        return url


class MemoryFS(object):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def upload(self, data, mime_type, key=None):
        key = key or gen_salt(16)
        mc.set('%s:%s' % (self.bucket_name, key), data)
        return {}

    def get_url(self, key, is_private=False, expires=None):
        key = '%s:%s' % (self.bucket_name, key)
        return url_for('webtest.images', key=key, _external=True)


class UploadError(Exception):
    pass


def make_filestore(bucket_name, *args, **kwargs):
    if DEBUG:
        return MemoryFS(bucket_name)
    else:
        return QiniuFS(bucket_name, *args, **kwargs)


fs = make_filestore('guihua-article', 'https://dn-ghimg.qbox.me')
