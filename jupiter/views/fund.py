# coding: utf-8

from flask import Blueprint, g, redirect
from flask_mako import render_template

from core.models.article.fundweekly import FundWeekly
from core.models.fund.group import Group
from core.models.fund.subscription import Subscription
from core.models.article.consts import FUNDWEEKLY_CATEGORY

bp = Blueprint('fund', __name__)
_PER_PAGE = 20


@bp.route('/fund')
def home():
    cur_path = 'fund'
    groups_without_like = Group.paginate()
    user_like_count = Subscription.get_user_count()
    if not g.user:
        return render_template('fund/index.html', **locals())

    # 取用户like的组合
    likes = Subscription.get_by_user(g.user.id)

    groups = []
    for group in groups_without_like:
        group.is_liked = False
        arts = FundWeekly.get_articles_by_category(category=group.id, limit=1)
        if len(arts):
            group.article = arts[0]
        for like in likes:
            if str(group.id) == str(like.group_id):
                group.is_liked = True
                break
        groups.append(group)

    return render_template('fund/user.html', **locals())


@bp.route('/fund/<int:id>', defaults={'follow': False})
@bp.route('/fund/<int:id>/follow', defaults={'follow': True})
def detail(id, follow=False):
    cur_path = 'fund'
    group = Group.get(id)
    funds = group.get_funds_m2m()
    if g.user:
        is_liked = Subscription.is_like(group.id, g.user.id)
    if not group:
        return redirect('/')

    # 读取周报
    weeklys = FundWeekly.get_articles_by_category(category=group.id, limit=2)
    return render_template('fund/detail.html', **locals())


@bp.route('/fund/weekly/<int:id>')
def weekly(id):
    cur_path = 'fund'
    article = FundWeekly.get(id)
    if not article:
        return redirect('/')
    if g.user:
        article.mark_as_read(g.user.id)
    is_article_fund = True
    return render_template('viewpoints/fundweekly_detail.html', **locals())


@bp.route('/fund/weekly/category/<category>', defaults={'num': 0})
@bp.route('/fund/weekly/category/<category>/<int:num>')
def weekly_cat(category, num):
    # by category
    cur_path = 'fund'
    start = num * _PER_PAGE
    articles = FundWeekly.get_articles_by_category(
        category=category, start=start, limit=_PER_PAGE)
    if not articles:
        return redirect('/')
    total = FundWeekly.get_count_by_category(category)
    category_name = FUNDWEEKLY_CATEGORY.get(category)
    is_article_fund = True
    return render_template('viewpoints/fundweekly.html', **locals())
