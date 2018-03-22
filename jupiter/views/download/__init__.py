from __future__ import print_function, absolute_import, unicode_literals

from datetime import timedelta
from pkg_resources import parse_version

from flask import Blueprint, abort, redirect, request, url_for
from more_itertools import first

from jupiter.utils.inhouse import check_is_inhouse
from core.models.download import Project, Release
from core.models.download.project import obtain_public_version
from core.models.download.consts import ANDROID_APP_NAME
from libs.fs.fs import make_filestore
from libs.logger.rsyslog import rsyslog


bp = Blueprint('download', __name__)
BASE_URLS = {
    'guihua-download': 'https://dn-guihua-dl.qbox.me',
}
MARKET_URLS = {
    'itunes': 'https://itunes.apple.com/cn/app/id1054855822',
    'myapp': 'http://a.app.qq.com/o/simple.jsp?pkgname=com.haoguihua.app',
}


@bp.route('/download/<project_name>/<version>')
@bp.route('/download/<project_name>/latest')
def download(project_name, version=None):
    project = Project.get_by_name(project_name) or abort(404)
    releases = project.list_releases()

    # strips draft
    if not version:
        releases = (
            r for r in releases if r.status is not Release.Status.draft)

    # strips inhouse
    if not check_is_inhouse():
        releases = (
            r for r in releases if r.status is not Release.Status.inhouse)

    # chooses version
    if version is None:
        release = max(releases, key=obtain_public_version)
    else:
        releases = (
            r for r in releases
            if obtain_public_version(r) == parse_version(version))
        release = first(releases, None)

    if not release:
        abort(404)
    if release.status is Release.Status.absent:
        abort(410)
    else:
        fs = make_filestore(project.bucket_name, BASE_URLS[project.bucket_name])
        url = fs.get_url(
            release.file_path, is_private=True, expires=timedelta(minutes=30))
        rsyslog.send(release.file_path, tag='download_release')
        return redirect(url)


@bp.route('/app/download/latest')
@bp.route('/app/download/<version>')
def download_app(version=None):
    if request.user_agent.is_weixin_browser:
        # terrible weixin blocks all links to other markets.
        target = 'myapp'
    elif request.user_agent.platform in ('iphone', 'ipad'):
        target = 'itunes'
    else:
        target = request.args.get('target')
        if target not in MARKET_URLS:
            target = None

    if target:
        return redirect(MARKET_URLS[target])

    return redirect(url_for(
        'download.download', project_name=ANDROID_APP_NAME, version=version))
