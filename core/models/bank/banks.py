# coding: utf-8

from .bank import BankCollection
from .partners import Partner

bank_collection = BankCollection(suites={
    Partner.yxpay: ['yxpay_id'],
    Partner.yrd: ['yxlib_id', 'yxlib_amount_limit'],
    Partner.zs: ['zslib_id', 'zslib_amount_limit'],
    Partner.zw: ['zwlib_id', 'zwlib_amount_limit'],
    Partner.xm: ['xm_id', 'xmlib_amount_limit'],
    Partner.sxb: ['sxb_id', 'sxblib_amount_limit'],
})

bank_collection.add_bank(
    id_='6',
    name=u'招商银行',
    telephone='95555',
    aliases=[],
    yxlib_id='6',
    yxlib_amount_limit=(5000, 50000),
    yxpay_id='0308',
    zslib_id='0005',
    zslib_amount_limit=1000,
    zwlib_id='6',
    zwlib_amount_limit=(50000, 50000),
    xm_id='0308',
    xmlib_amount_limit=(50000, 5000000),
    sxb_id='0308',
    sxblib_amount_limit=(50000, 5000000)
    )
bank_collection.add_bank(
    id_='4',
    name=u'建设银行',
    telephone='95533',
    aliases=[u'中国建设银行'],
    yxlib_id='4',
    yxlib_amount_limit=(10000, 10000),
    yxpay_id='0105',
    zslib_id='0003',
    zslib_amount_limit=50000,
    zwlib_id='4',
    zwlib_amount_limit=(50000, 50000),
    xm_id='0105',
    xmlib_amount_limit=(200000, 2000000),
    sxb_id='0105',
    sxblib_amount_limit=(200000, 2000000)
    )
bank_collection.add_bank(
    id_='5',
    name=u'中国银行',
    telephone='95566',
    aliases=[],
    yxlib_id='5',
    yxlib_amount_limit=(10000, 10000),
    yxpay_id='0104',
    zslib_id='0004',
    zslib_amount_limit=50000,
    zwlib_id='5',
    zwlib_amount_limit=(50000, 50000),
    xm_id='0104',
    xmlib_amount_limit=(50000, 200000),
    sxb_id='0104',
    sxblib_amount_limit=(50000, 200000)
    )
bank_collection.add_bank(
    id_='3',
    name=u'农业银行',
    telephone='95599',
    aliases=[u'中国农业银行'],
    yxlib_id='3',
    yxlib_amount_limit=(10000, 100000),
    yxpay_id='0103',
    zslib_id='0002',
    zslib_amount_limit=20000,
    zwlib_id='3',
    zwlib_amount_limit=(500000, 500000),
    xm_id='0103',
    xmlib_amount_limit=(500000, 1000000),
    sxb_id='0103',
    sxblib_amount_limit=(500000, 1000000)
    )
bank_collection.add_bank(
    id_='7',
    name=u'民生银行',
    telephone='95568',
    aliases=[u'中国民生银行'],
    yxlib_id='7',
    yxlib_amount_limit=(5000, 5000),
    yxpay_id='0305',
    zslib_id='0016',
    zslib_amount_limit=50000,
    zwlib_id='7',
    zwlib_amount_limit=(100000, 500000),
    xm_id='0305',
    xmlib_amount_limit=(100000, 1000000),
    sxb_id='0305',
    sxblib_amount_limit=(100000, 1000000)
    )
bank_collection.add_bank(
    id_='14',
    name=u'光大银行',
    telephone='95595',
    aliases=[u'中国光大银行'],
    yxlib_id='14',
    yxlib_amount_limit=(5000, 5000),
    yxpay_id='0303',
    zslib_id='0007',
    zslib_amount_limit=50000,
    zwlib_id='13',
    zwlib_amount_limit=(100000, 500000),
    xm_id='0303',
    xmlib_amount_limit=(100000, 1000000),
    sxb_id='0303',
    sxblib_amount_limit=(100000, 1000000)
    )
bank_collection.add_bank(
    id_='9',
    name=u'浦发银行',
    telephone='95528',
    aliases=[u'浦东发展银行'],
    yxlib_id='9',
    yxlib_amount_limit=(20000, 100000),
    yxpay_id='0310',
    zslib_id='0009',
    zslib_amount_limit=50000,
    zwlib_id='14',
    zwlib_amount_limit=(20000, 50000),
    xm_id='0310',
    xmlib_amount_limit=(50000, 350000),
    sxb_id='0310',
    sxblib_amount_limit=(50000, 350000)
    )
bank_collection.add_bank(
    id_='1',
    name=u'工商银行',
    telephone='95588',
    aliases=[u'中国工商银行'],
    yxlib_id='1',
    yxlib_amount_limit=(5000, 5000),
    yxpay_id='0102',
    zslib_id='0001',
    zslib_amount_limit=50000,
    zwlib_id='2',
    zwlib_amount_limit=(50000, 50000),
    xm_id='0102',
    xmlib_amount_limit=(500000, 500000),
    sxb_id='0102',
    sxblib_amount_limit=(500000, 500000)
    )
bank_collection.add_bank(
    id_='10001',
    name=u'兴业银行',
    telephone='95561',
    aliases=[],
    yxpay_id='0309',
    zslib_id='0006',
    zslib_amount_limit=50000,
    zwlib_id='1',
    zwlib_amount_limit=(50000, 50000),
    xm_id='0309',
    xmlib_amount_limit=(50000, 350000),
    sxb_id='0309',
    sxblib_amount_limit=(50000, 350000)
    )
bank_collection.add_bank(
    id_='10002',
    name=u'中信银行',
    telephone='95558',
    aliases=[],
    yxpay_id='0302',
    zslib_id='0008',
    zslib_amount_limit=50000,
    zwlib_id='9',
    zwlib_amount_limit=(100000, 500000),
    xm_id='0302',
    xmlib_amount_limit=(100000, 1000000),
    sxb_id='0302',
    sxblib_amount_limit=(100000, 1000000)
    )
bank_collection.add_bank(
    id_='10003',
    name=u'交通银行',
    telephone='95559',
    aliases=[],
    yxpay_id='0301',
    zslib_id='0010',
    zslib_amount_limit=50000,
    zwlib_id='8',
    zwlib_amount_limit=(10000, 10000),
    xm_id='0301',
    xmlib_amount_limit=(10000, 100000),
    sxb_id='0301',
    sxblib_amount_limit=(10000, 100000)
    )
bank_collection.add_bank(
    id_='10004',
    name=u'邮政储蓄银行',
    telephone='95580',
    aliases=[u'邮储银行'],
    yxpay_id='0100',
    zslib_id='0011',
    zslib_amount_limit=50000,
    zwlib_id='15',
    zwlib_amount_limit=(5000, 5000),
    xm_id='0100',
    xmlib_amount_limit=(50000, 350000),
    sxb_id='0100',
    sxblib_amount_limit=(50000, 350000)
    )
bank_collection.add_bank(
    id_='10005',
    name=u'平安银行',
    telephone='95511',
    aliases=[],
    yxpay_id='0307',
    zslib_id='0012',
    zslib_amount_limit=50000,
    zwlib_id='12',
    zwlib_amount_limit=(200000, 500000),
    xm_id='0307',
    xmlib_amount_limit=(200000, 1000000),
    sxb_id='0307',
    sxblib_amount_limit=(200000, 1000000)
    )
bank_collection.add_bank(
    id_='10006',
    name=u'上海银行',
    telephone='95594',
    aliases=[],
    yxpay_id='0401',
    zslib_id='0013',
    zslib_amount_limit=50000)
bank_collection.add_bank(
    id_='10007',
    name=u'北京银行',
    telephone='95526',
    aliases=[],
    yxpay_id='0403',
    zslib_id='0014',
    zslib_amount_limit=5000,
    zwlib_id='11',
    zwlib_amount_limit=(10000000, 10000000),
    )
bank_collection.add_bank(
    id_='10008',
    name=u'广东发展银行',
    telephone='95508',
    aliases=[],
    yxpay_id='0306',
    zslib_id='0015',
    zslib_amount_limit=50000,
    zwlib_id='16',
    zwlib_amount_limit=(100000, 500000),
    xm_id='0306',
    xmlib_amount_limit=(100000, 1000000),
    sxb_id='0306',
    sxblib_amount_limit=(100000, 1000000)
    )

bank_collection.add_bank(
    id_='10009',
    name=u'华夏银行',
    telephone='',
    aliases=[],
    xm_id='0304',
    xmlib_amount_limit=(100000, 200000),
    sxb_id='0304',
    sxblib_amount_limit=(100000, 200000)
    )

# 还木有任何产品支持的银行
bank_collection.add_bank(
    id_='10010',
    name=u'深圳发展银行',
    telephone='',
    aliases=[])
bank_collection.add_bank(
    id_='20000',
    name=u'农村信用合作社',
    telephone='',
    aliases=[
        u'广东省农村信用社联合社',
    ])
