# coding: utf-8

import datetime

from core.models.download import Project, Release
from core.models.site import Announcement
from libs.utils.log import bcolors


def add_download():
    project = Project.add('guihua-android', u'好规划 Android App')

    r1 = project.add_release(
        '0001', '0.1.0', 'b3799c5ff83840a350ca4376eccebb1965c418b1.apk')
    r2 = project.add_release(
        '0002', '0.2.0', '15b7aea3695dbde7334eb6ac264edfd76976fef6.apk')
    r3 = project.add_release(
        '0003', '0.2.1', '109625e5a6414aea08a72519d5eb0848311d7ae4.apk')

    r1.transfer_status(Release.Status.absent)
    r2.transfer_status(Release.Status.inhouse)
    r3.transfer_status(Release.Status.public)

    template = u'{0.project.display_name}\t{0.display_version}\t{0.status.name}'
    for r in project.list_releases():
        bcolors.run(template.format(r).encode('utf-8'), key='site.download')


def add_announcement():
    start_time = datetime.datetime.now() - datetime.timedelta(days=1)
    stop_time = datetime.datetime.now() + datetime.timedelta(days=1)

    announcement = Announcement.add(
        subject=u'开发和测试环境',
        subject_type=Announcement.SubjectType.notice,
        content=u'您现在在**开发和测试环境**中, 任何修改都不会影响生产环境',
        content_type=Announcement.ContentType.markdown,
        start_time=start_time,
        stop_time=stop_time,
        endpoint='*')

    bcolors.run(repr(announcement), key='site.announcement')


def main():
    add_download()
    add_announcement()


if __name__ == '__main__':
    main()
