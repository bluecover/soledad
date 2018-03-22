# coding: utf-8

from flask import redirect, g, Blueprint, request
from flask_mako import render_template
from werkzeug.contrib.atom import AtomFeed

from jupiter.utils.inhouse import check_is_inhouse
from core.models.article.article import Article
from core.models.article.viewpoint import ViewPoint
from core.models.article.question import Question
from core.models.article.consts import VIEWPOINT_CATEGORY


bp = Blueprint('article', __name__)

_PER_PAGE = 20
_FEED_LIMIT = 50


@bp.route('/viewpoints', defaults={'num': 0})
@bp.route('/viewpoints/page/<int:num>')
def viewpoints(num):
    cur_path = 'viewpoints'
    start = num * _PER_PAGE
    articles = ViewPoint.get_all(start=start, limit=_PER_PAGE)
    total = ViewPoint.get_count()
    return render_template('viewpoints/viewpoints.html', **locals())


@bp.route('/viewpoints/feed')
def viewpoints_feed():
    viewpoints = ViewPoint.get_all(limit=_FEED_LIMIT)
    feed = make_viewpoint_feed(viewpoints)
    return feed.get_response()


@bp.route('/viewpoints/category/<category>', defaults={'num': 0})
@bp.route('/viewpoints/category/<category>/<int:num>')
def viewpoints_category(category, num):
    # by category
    cur_path = 'viewpoints'
    start = num * _PER_PAGE
    articles = ViewPoint.get_articles_by_category(
        category, start=start, limit=_PER_PAGE)
    if not articles:
        return redirect('/')
    total = ViewPoint.get_count_by_category(category)
    category_name = VIEWPOINT_CATEGORY.get(category)
    return render_template('viewpoints/viewpoints.html', **locals())


@bp.route('/viewpoints/category/<category>/feed')
def viewpoints_category_feed(category):
    viewpoints = ViewPoint.get_articles_by_category(
        category, limit=_FEED_LIMIT)
    category_name = VIEWPOINT_CATEGORY.get(category)
    feed = make_viewpoint_feed(viewpoints, category_name)
    return feed.get_response()


@bp.route('/consultations', defaults={'num': 0})
@bp.route('/consultations/page/<int:num>')
def consultations(num):
    cur_path = 'consultations'
    start = num * _PER_PAGE
    articles = Question.get_all(start=start, limit=_PER_PAGE)
    total = Question.get_count()
    return render_template('viewpoints/consultations.html', **locals())


@bp.route('/<article_type>/<int:id>')
def article_detail(article_type, id):
    cur_path = 'viewpoints'
    if article_type not in ('viewpoints', 'consultations',):
        return redirect('/')
    if article_type in ('consultations',):
        return redirect('/consultations')

    article = Article.get(id)
    if not isinstance(article, ViewPoint):
        return redirect('/consultations')

    if not article or not article.is_published():
        if can_view_unpublished_article():
            return redirect('/')
    if not article:
        return redirect('/')
    return render_template('viewpoints/viewdetail.html', **locals())


def can_view_unpublished_article():
    return g.user and check_is_inhouse()


def make_viewpoint_feed(viewpoints, category_name=None):
    title = ViewPoint.kind_cn
    if category_name:
        title = '%s - %s' % (title, category_name)

    feed_entries = [v.make_feed_entry() for v in viewpoints]
    feed = AtomFeed(
        title, feed_url=request.url, url=request.host_url,
        entries=feed_entries)

    return feed
