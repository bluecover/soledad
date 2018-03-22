# coding: utf-8

from flask import Blueprint
from flask_mako import render_template

from jupiter.utils.inhouse import check_is_inhouse
from core.models.download import Project


bp = Blueprint('app', __name__)


@bp.route('/app')
def index():
    project = Project.get_by_name('guihua-android')
    release = project.get_latest_release(include_inhouse=check_is_inhouse())

    return render_template('app/app_download.html', **locals())
