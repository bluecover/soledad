#!/usr/bin/env python
# -*- coding:utf-8 -*-

from plan import Plan as _Plan
from envcfg.json.solar import DEBUG


class Plan(_Plan):

    @property
    def cron_content(self):
        env = '. /etc/default/solar-solar'
        commands = '\n'.join((
            '{job.time_in_cron_syntax} {shell_prefix} && '
            '{job.task_in_cron_syntax}').format(job=job, shell_prefix=env)
            for job in self.jobs)
        return '{0.comment_begin}\n{1}\n{0.comment_end}\n'.format(
            self, commands)


yixin_cron = Plan('yixin')
zhiwang_cron = Plan('zhiwang')
xm_cron = Plan('xinmi')
sxb_cron = Plan('sxb')
placebo_cron = Plan('placebo')
data_cron = Plan('data')
fund_cron = Plan('fund')
wallet_cron = Plan('wallet')
oauth_cron = Plan('oauth')
welfare_cron = Plan('welfare')
pusher_cron = Plan('pusher')


# 同步宜人贷订单最新支付/确认状态
yixin_cron.script(
    '-m crons.yixin.cron_hoard_order_exited', every='1.day', at='09:30 17:30')
yixin_cron.script(
    '-m crons.yixin.cron_sync_order_status', every='30.minute')
yixin_cron.script(
    '-m crons.yixin.cron_hoard_order_sync', every='1.day', at='1:00 7:00 13:00 19:00')


# 从mass取每日净值，并且计算收益（包括用户收益）
# fund_cron.script('-m crons.mass.sync_data', every='1.day', at='09:30')


# 指旺

# 正常时段（每隔10分钟）更新指旺产品列表
zhiwang_cron.script(
    '-m crons.zhiwang.cron_updating_products', every='10.minute')
# 高峰时段高频(11点1分-59分，每隔一分钟，除10分20分等正常更新时间点)更新产品信息
zhiwang_cron.script(
    '-m crons.zhiwang.cron_updating_products', every='1.day',
    at=' '.join(['11:%s' % minute for minute in range(1, 60) if minute % 10 != 0]))

# 同步指旺订单最新支付/确认状态
zhiwang_cron.script(
    '-m crons.zhiwang.cron_sync_order_status', every='9.minute')
# 获取指旺资产退出情况
zhiwang_cron.script(
    '-m crons.zhiwang.cron_check_asset_exit', every='1.day',
    at='07:30 09:00 10:30 13:00 14:30 16:00 17:30 19:00')

# 同步薪结算投米订单最新支付/确认状态
xm_cron.script(
    '-m crons.xinmi.cron_sync_order_status', every='5.minute')
xm_cron.script(
    '-m crons.xinmi.cron_updating_products', every='1.minute')


# 随心宝

# 正常时段（每隔10分钟）更新随心宝产品列表
sxb_cron.script(
    '-m crons.hoarder.cron_updating_sxb_products', every='10.minute')
# 高峰时段高频(10点1分-59分, 11点1分-59分，每隔一分钟，除10分20分等正常更新时间点)更新产品信息
sxb_cron.script(
    '-m crons.hoarder.cron_updating_sxb_products', every='1.day',
    at=' '.join(['10:%s' % minute for minute in range(1, 60) if minute % 10 != 0]))
sxb_cron.script(
    '-m crons.hoarder.cron_updating_sxb_products', every='1.day',
    at=' '.join(['11:%s' % minute for minute in range(1, 60) if minute % 10 != 0]))
sxb_cron.script(
    '-m crons.hoarder.cron_sync_order_status', every='5.minute')
sxb_cron.script(
    '-m crons.hoarder.cron_sync_asset_status', every='1.day', at='00:30')

# 零钱包
wallet_cron.script(
    '-m crons.wallet.cron_annual_rates', every='1.day',
    at='2:00 6:00')
wallet_cron.script(
    '-m crons.wallet.cron_user_profit', every='1.day',
    at='2:00 6:00')
# wallet_cron.script(
#     '-m crons.wallet.synchronize_with_zhongshan', every='1.day', at='12:00')

# 优惠
welfare_cron.script(
    '-m crons.welfare.cron_distribute_birthday_package', every='1.day', at='09:00')

# OAuth API
oauth_cron.script(
    '-m jupiter.cli oauth vacuum_tokens -g 60', every='1.day', at='3:00')

# 体验金
placebo_cron.script(
    '-m crons.placebo.cron_exiting', every='1.day', at='10:00')

# 通知推送
pusher_cron.script(
    '-m crons.pusher.cron_inactive_saver_wakeup', every='10.day', at='10:00')
pusher_cron.script(
    '-m crons.pusher.cron_coupon_expiration_reminder', every='1.day', at='11:00')


def main():
    if DEBUG:
        yixin_cron.run('check')
        zhiwang_cron.run('check')
        xm_cron.run('check')
        sxb_cron.run('check')
        placebo_cron.run('check')
        data_cron.run('check')
        fund_cron.run('check')
        wallet_cron.run('check')
        oauth_cron.run('check')
        welfare_cron.run('check')
        pusher_cron.run('check')
    else:
        yixin_cron.run('update')
        zhiwang_cron.run('update')
        xm_cron.run('update')
        sxb_cron.run('update')
        placebo_cron.run('update')
        data_cron.run('update')
        fund_cron.run('update')
        wallet_cron.run('update')
        oauth_cron.run('update')
        welfare_cron.run('update')
        pusher_cron.run('update')


if __name__ == '__main__':
    main()
