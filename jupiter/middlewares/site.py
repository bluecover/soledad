# coding: utf-8

from __future__ import absolute_import

from datetime import date

from flask import Blueprint, has_request_context, request

from jupiter.utils.inhouse import check_is_inhouse
from core.models.download import Project
from core.models.site import Announcement


bp = Blueprint('middlewares.site', __name__)


@bp.app_context_processor
def guihua_android_release():
    if not request:
        return {}
    project = Project.get_by_name('guihua-android')
    release = project.get_latest_release(include_inhouse=check_is_inhouse())
    return {'guihua_android_latest': release}


@bp.app_context_processor
def announcements():
    if not request:
        return {}
    announcements = Announcement.get_multi_by_date(date.today())
    if has_request_context():
        announcements = [a for a in announcements if a.is_suitable(request)]
    return {'announcements': announcements}
