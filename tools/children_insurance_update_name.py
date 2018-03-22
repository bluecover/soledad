# -*- coding: utf-8 -*-

"""
儿童保险计划更新
"""

from libs.db.store import db
from core.models.insurance.packages import Package
from core.models.insurance.insurance import Insurance


def update_insurance(id_, ins_title, urls):
    """
    更新insurance 的名称 和 链接
    """
    ins = Insurance.get(id_)

    db.execute('update insurance set name=%s where insurance_id=%s', (ins_title, id_,))
    db.commit()
    Insurance.clear_cache(id_)
    feerate = ins.ins_property.feerate[:]
    rec_reason = ins.ins_property.rec_reason
    buy_url = urls
    ins_title = ins_title
    ins_sub_title = ins.ins_property.ins_sub_title
    ins.add_insurance_props(
        feerate, rec_reason, buy_url, ins_title, ins_sub_title)

    print '更新insurance %s 的标题...成功' % ins_title


def update_package(ins_id, ins_title):
    db.execute('update insurance_package set insurance_name=%s where insurance_id=%s',
               (ins_title, ins_id,))
    db.commit()
    for package_id in Package.get_by_insurance_id(ins_id):
        Package.clear_cache(package_id)

    print '更新package %s ... 成功' % ins_title


if __name__ == '__main__':
    """
    儿童险两款中国人寿产品，更换为中民链接，名称有所改变，内容不变。
    慧择少儿学生安康保障计划（国寿版） 计划B    260元
    更换为 中国人寿阳光宝贝保障计划A
    带识别参数链接：
    http://www.zhongmin.cn/AutoRedirect_1.aspx?source=21013&url=http://www.zhongmin.cn/Health/
    product/AccidProduct.aspx?id=350&age=0&sex=0&span=0&money=50000

    慧择少儿学生安康保障计划（国寿版） 计划A  190元
    更换为 中国人寿安心学生吉祥保障计划
    带识别参数链接：
    http://www.zhongmin.cn/AutoRedirect_1.aspx?source=21013&url=http://www.zhongmin.cn/Health/
    product/AccidProduct.aspx?id=349&age=3&sex=0&span=0&money=20000
    """
    update_package(4, '中国人寿阳光宝贝保障计划A')
    update_insurance(4, '中国人寿阳光宝贝保障计划A',
                     'http://www.zhongmin.cn/AutoRedirect_1.aspx?source=21013&url=http://www.'
                     'zhongmin.cn/Health/product/AccidProduct.aspx?id=350&age=0&sex=0&span=0&'
                     'money=50000')
    update_package(3, '中国人寿安心学生吉祥保障计划')
    update_insurance(3, '中国人寿安心学生吉祥保障计划',
                     'http://www.zhongmin.cn/AutoRedirect_1.aspx?source=21013&url=http://www.'
                     'zhongmin.cn/Health/product/AccidProduct.aspx?id=349&age=3&sex=0&span=0&'
                     'money=20000')
