# -*- coding: utf-8 -*-


import datetime
import calendar


class Age(object):
    def __init__(self, birthday):
        self.birth = self.calculate_age(birthday)

    def calculate_age(self, birthday):
        return self.__calculate_age(
            datetime.datetime.strptime(birthday, '%Y-%m-%d'))

    def __calculate_age(self, born):
        today = datetime.date.today()
        year = today.year - born.year - (
            (today.month, today.day) < (born.month, born.day))
        dateyear = today.year - (
            (today.month, today.day) < (born.month, born.day))

        # 针对闰年处理
        if not calendar.isleap(dateyear) or born.month != 2 or born.day <= 28:
            days = (today - datetime.date(dateyear, born.month, born.day)).days
        else:
            days = (today - datetime.date(dateyear, 2, 28)).days

        return (year, days)
