# coding: utf-8

from pytest import raises

from core.models.download import Project, Release
from .framework import BaseTestCase


class DownloadTest(BaseTestCase):

    def test_get_nothing(self):
        assert not Project.get(42)
        assert not Project.get_by_name('hitchhikers')

    def test_add(self):
        project = Project.add('hitchhikers', u'漫游者')
        assert project.name == 'hitchhikers'
        assert project.display_name == u'漫游者'
        assert project.bucket_name == 'guihua-download'
        assert project.creation_time

    def test_get(self):
        project = Project.add('hitchhikers', u'漫游者')
        assert project == Project.get(project.id_)
        assert project == Project.get_by_name('hitchhikers')

    def test_rename(self):
        project = Project.add('hitchhikers', u'漫游者')
        project.edit_display_name(u'银河系漫游者')
        assert project.display_name == u'银河系漫游者'

        project = Project.get(project.id_)
        assert project.display_name == u'银河系漫游者'

    def test_release(self):
        project = Project.add('hitchhikers', u'漫游者')
        assert project.list_releases() == []

        release = project.add_release('0001', '0.1.0', 'foobar')
        assert project.list_releases() == [release]
        assert project.get_latest_release() is None
        assert project.get_latest_release(include_inhouse=True) is None
        assert project.get_latest_release(include_draft=True) == release
        assert release.file_path == 'hitchhikers/foobar'
        assert release.status is Release.Status.draft
        assert release.display_version == u'0.1.0 (0001)'

        second_release = project.add_release('0002', '0.2.0', 'aaabbb')
        assert project.list_releases() == [release, second_release]
        assert project.get_latest_release() is None
        release.transfer_status(Release.Status.public)
        assert project.get_latest_release() == release
        assert project.get_latest_release(include_inhouse=True) == release
        assert project.get_latest_release(include_draft=True) == second_release

    def test_release_status(self):
        project = Project.add('hitchhikers', u'漫游者')
        release = project.add_release('0001', '0.1.0', 'foo')
        second_release = project.add_release('0002', '0.2.0', 'bar')
        third_release = project.add_release('0003', '0.2.1', 'baz')

        # initial
        assert release.status is Release.Status.draft
        assert second_release.status is Release.Status.draft
        assert third_release.status is Release.Status.draft

        # [pass] draft -> inhouse
        assert release.can_transfer_status(Release.Status.inhouse)
        release.transfer_status(Release.Status.inhouse)
        assert release.status is Release.Status.inhouse

        # [fail] inhouse -> draft
        assert not release.can_transfer_status(Release.Status.draft)
        with raises(ValueError):
            release.transfer_status(Release.Status.draft)
        assert release.status is Release.Status.inhouse

        # [pass] inhouse -> public
        assert release.can_transfer_status(Release.Status.public)
        release.transfer_status(Release.Status.public)
        assert release.status is Release.Status.public

        # [fail] public -> absent
        assert not release.can_transfer_status(Release.Status.absent)
        with raises(ValueError):
            release.transfer_status(Release.Status.absent)
        assert release.status is Release.Status.public

        # [pass] draft -> absent
        assert second_release.can_transfer_status(Release.Status.absent)
        second_release.transfer_status(Release.Status.absent)
        assert second_release.status is Release.Status.absent

        # [pass] inhouse -> absent
        assert third_release.can_transfer_status(Release.Status.inhouse)
        assert third_release.can_transfer_status(Release.Status.public)
        third_release.transfer_status(Release.Status.inhouse)
        assert third_release.can_transfer_status(Release.Status.absent)
        third_release.transfer_status(Release.Status.absent)
        assert third_release.status is Release.Status.absent

        # [fail] absent -> public
        assert not third_release.can_transfer_status(Release.Status.public)
