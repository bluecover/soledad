# coding: utf-8

from flask import jsonify, g, Blueprint
from core.models.fund.income import Income
from core.models.fund.incomeuser import IncomeUser
from core.models.fund.group import Group
from core.models.fund.subscription import Subscription
from core.models.article.fundweekly import FundWeekly

bp = Blueprint('jfund', __name__, url_prefix='/j/fund')


@bp.route('/like/<int:group_id>')
def like(group_id):
    if not g.user:
        return '0'
    result = Subscription.like_group(group_id, g.user.id)
    if result:
        return jsonify(r=True)
    else:
        return jsonify(r=False)


@bp.route('/income_chart/<int:group_id>')
def income_chart(group_id):
    """ 取得一个基金组合的收益率 """
    incomes = Income.get_near_day(group_id, 1000)[::-1]
    group = Group.get(group_id)
    data = []
    least_income = 0
    for income in incomes:
        data.append({
            'id': income.id,
            'group_id': income.group_id,
            'day': income.day.strftime('%Y-%m-%d'),
            'income': income.income,
            'income_stock': income.income_stock,
        })
        least_income = income.income
    return jsonify(r=True,
                   data=data,
                   group_subject=group.subject,
                   group_created=group.create_time.strftime('%Y-%m-%d'),
                   group_income=least_income)


@bp.route('/income_user_chart2/')
def income_user_chart2():
    """ 取得用户的基金组合关注收益率 for new chart """
    if not g.user:
        return jsonify(r=False)

    likes = Subscription.get_by_user(g.user.id)
    info = []
    incomes = []
    jincomes = {}
    for like in likes:
        least_income = None
        incomes = IncomeUser.get_near_day(like.group_id, g.user.id, 7)[::-1]
        for income in incomes:
            key = str(income.day)[5:].replace('-', '/')
            if not jincomes.get(key):
                jincomes[key] = {}
            jincomes[key][str(income.group_id)] = income.income
            least_income = income.income
        group = Group.get(like.group_id)
        arts = FundWeekly.get_articles_by_category(category=group.id, limit=1)
        if len(arts):
            group.article = arts[0]
        gjson = {
            'group_id': like.group_id,
            'group_subject': group.subject,
            # 'group_total_income': group.total_income,
            'like_date': like.create_time.strftime('%Y.%m.%d'),
            'group_yesterday_income': group.yesterday_income,
            'group_created': group.create_time.strftime('%Y.%m.%d'),
            'group_income': least_income,
            'group_article': group.article.id if hasattr(group, 'article') else None,
            'group_article_read':
            group.article.has_read(g.user.id) if hasattr(group, 'article') else None,
        }
        info.append(gjson)

    return jsonify(r=True, info=info, incomes=jincomes)


@bp.route('/income_user_chart/')
def income_user_chart():
    """ 取得用户的基金组合关注收益率 """
    if not g.user:
        return jsonify(r=False)

    likes = Subscription.get_by_user(g.user.id)
    user_incomes = []
    for like in likes:
        incomes = IncomeUser.get_near_day(like.group_id, g.user.id, 7)[::-1]
        group = Group.get(like.group_id)
        arts = FundWeekly.get_articles_by_category(category=group.id, limit=1)
        if len(arts):
            group.article = arts[0]
        like_income = {
            'like_date': like.create_time.strftime('%Y.%m.%d'),
            'group_id': like.group_id,
            'group_subject': group.subject,
            # 'group_total_income': group.total_income,
            'group_yesterday_income': group.yesterday_income,
            'group_created': group.create_time.strftime('%Y.%m.%d'),
            'group_article': group.article.id if hasattr(group, 'article') else None,
            'group_article_read':
            group.article.has_read(g.user.id) if hasattr(group, 'article') else None,
            'data': [],
        }
        for income in incomes:
            like_income['data'].append({
                'id': income.id,
                'group_id': income.group_id,
                'day': income.day.strftime('%Y-%m-%d'),
                'income': income.income
            })
        user_incomes.append(like_income)

    return jsonify(r=True, incomes=user_incomes)
