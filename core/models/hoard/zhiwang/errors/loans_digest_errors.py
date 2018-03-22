# coding:utf-8


class FetchLoansDigestError(Exception):
    def __unicode__(self):
        return u'抱歉，暂未获得相关信息，将于交易确认后四个工作日内确认。'
