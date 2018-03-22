from flask import request, g
from flask.ext.mako import render_template
from ._blueprint import create_blueprint
from core.models.insurance.plan import Plan


bp = create_blueprint('products', __name__)


@bp.route('/product/A001/')
def products_zhongmin():
    redirect_url = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?' \
        'source=21013&url=http://www.zhongmin.cn/accid/Product/accident662.html'

    redirect_url_1 = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?' \
        'source=21013&url=http://www.zhongmin.cn/Travel/Product/travel12-18d1.html'

    redirect_url_2 = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?' \
        'source=21013&url=http://www.zhongmin.cn/Travel/Product/travel9-18d1.html'

    if request.user_agent.is_mobile:
        redirect_url = 'http://wap.zhongmin.cn/AutoRedirect_1.aspx?' \
                       'url=http://m.zhongmin.cn/WAP/GoodsDetail.aspx?bId=4&pId=662&source=21013'

        redirect_url_1 = 'http://wap.zhongmin.cn/AutoRedirect_1.aspx?' \
            'url=http://m.zhongmin.cn/WAP/GoodsDetail.aspx?bId=11&pId=12&source=21013'

        redirect_url_2 = 'http://wap.zhongmin.cn/AutoRedirect_1.aspx?' \
            'url=http://m.zhongmin.cn/WAP/GoodsDetail.aspx?bId=11&pId=9&source=21013'

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?' \
            'source=25997&url=http://www.zhongmin.cn/accid/Product/accident662.html'

    return render_template('/childins/A001.html', zhongmin_url=redirect_url,
                           redirect_url_1=redirect_url_1, redirect_url_2=redirect_url_2)


@bp.route('/product/A002/')
def products_a002():
    redirect_url = 'https://ssl.700du.cn/prod/slsywzx.html?inviter=0000025993'

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'https://ssl.700du.cn/prod/slsywzx.html?inviter=0000028825'

    return render_template('/childins/A002.html', redirect_url=redirect_url)


@bp.route('/product/A003/')
def products_a003():
    redirect_url = (
        'http://www.zhongmin.cn/AutoRedirect_1.aspx?'
        'source=21013&url=http://www.zhongmin.cn/Health/Product/'
        'HospitalProductT574-0-50-0.html')

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?source=25997' \
            '&url=http://www.zhongmin.cn/Health/Product/HospitalProductT574-0-50-0.html'

    return render_template('/childins/A003.html', redirect_url=redirect_url)


@bp.route('/product/L001/')
def products_l001():
    redirect_url = 'https://ssl.700du.cn/prod/jxyxjh.html?inviter=0000025993'

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'https://ssl.700du.cn/prod/jxyxjh.html?inviter=0000028825'

    return render_template('/childins/L001.html',
                           redirect_url=redirect_url)


@bp.route('/product/L002/')
def products_l002():
    redirect_url = ('http://www.zhongmin.cn/AutoRedirect_1.aspx?source=21013&url='
                    'http://www.zhongmin.cn/Regular/Product/RegularDetail13.html')

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?' \
            'source=25997&url=http://www.zhongmin.cn/Regular/Product/RegularDetail13.html'

    return render_template('/childins/L002.html',
                           redirect_url=redirect_url)


@bp.route('/product/CI001/')
def products_ci001():
    redirect_url = 'https://ssl.700du.cn/prod/xhijk.html?inviter=0000025993'

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'https://ssl.700du.cn/prod/xhijk.html?inviter=0000028825'

    return render_template('/childins/CI001.html', redirect_url=redirect_url)


@bp.route('/product/CI002/')
def products_ci002():
    redirect_url = ('https://ssl.700du.cn/prod/xhita.html?inviter=0000025993')

    # todo
    # if g.user and Plan.get_user_plan_dict(g.user.id):
    #     redirect_url = 'xxx'

    return render_template('/childins/CI002.html', redirect_url=redirect_url)


@bp.route('/product/CI003/')
def products_ci003():
    redirect_url = ('http://www.zhongmin.cn/AutoRedirect_1.aspx?'
                    'source=21013&url=http://www.zhongmin.cn/Health/product/AccidProduct.aspx?'
                    'id=75&age=0&sex=1&span=20&money=50000')

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?source=25997&' \
            'url=http://www.zhongmin.cn/Health/product/AccidProduct.aspx?' \
            'id=75&age=0&sex=1&span=20&money=50000'

    return render_template('/childins/CI003.html', redirect_url=redirect_url)


@bp.route('/product/CA003/')
def products_ca003():
    redirect_url = ('http://www.zhongmin.cn/AutoRedirect_1.aspx'
                    '?source=21013&url=http://www.zhongmin.cn/Health/Product/'
                    'HospitalProductT354-0-3-0.html')
    redirect_url_1 = 'http://cps.hzins.com/yk30459/product/detail-1198.html'

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?source=25997&' \
            'url=http://www.zhongmin.cn/Health/Product/HospitalProductT354-0-3-0.html'

    return render_template('/childins/CA003.html', redirect_url=redirect_url,
                           redirect_url_1=redirect_url_1)


@bp.route('/product/CA002/')
def products_ca002():
    redirect_url = ('http://www.zhongmin.cn/AutoRedirect_1.aspx'
                    '?source=21013&url=http://www.zhongmin.cn/'
                    'accid/Product/accident665.html')
    redirect_url_1 = 'http://cps.hzins.com/yk30459/product/detail-1198.html'

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?' \
            'source=25997&url=http://www.zhongmin.cn/accid/Product/accident665.html'

    return render_template('/childins/CA002.html', redirect_url=redirect_url,
                           redirect_url_1=redirect_url_1)


@bp.route('/product/CA001/')
def products_ca001():
    redirect_url = ('http://www.zhongmin.cn/AutoRedirect_1.aspx'
                    '?source=21013&url=http://www.zhongmin.cn/'
                    'accid/Product/accident626.html')
    redirect_url_1 = 'http://cps.hzins.com/yk30459/product/detail-1198.html'

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?' \
            'source=25997&url=http://www.zhongmin.cn/accid/Product/accident626.html'

    return render_template('/childins/CA001.html', redirect_url=redirect_url,
                           redirect_url_1=redirect_url_1)


@bp.route('/product/T001/')
def products_t001():
    redirect_url = ('http://www.zhongmin.cn/AutoRedirect_1.aspx?'
                    'source=21013&url=http://www.zhongmin.cn''/Travel/Product/travel11-18d1.html')

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?' \
            'source=25997&url=http://www.zhongmin.cn/Travel/Product/travel11-18d1.html'

    return render_template('/childins/T001.html', redirect_url=redirect_url)


@bp.route('/product/T002/')
def products_t002():
    redirect_url = ('http://www.zhongmin.cn/AutoRedirect_1.aspx?'
                    'source=21013&url=http://www.zhongmin.cn'
                    '/Travel/Product/travel8-18d7.html')

    if g.user and Plan.get_user_plan_dict(g.user.id):
        redirect_url = 'http://www.zhongmin.cn/AutoRedirect_1.aspx?'\
            'source=25997&url=http://www.zhongmin.cn/Travel/Product/travel8-18d7.html'

    return render_template('/childins/T002.html', redirect_url=redirect_url)
