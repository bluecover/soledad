# -*- coding: utf-8 -*-

# pylint: disable=E0602

income_month = (income_month_salary+income_month_extra) #月收入
expend_month = (expend_month_ent+expend_month_trans+expend_month_shopping+expend_month_house+expend_month_extra) #月支出
balance_month = (income_month-expend_month) #月结余
balance_month_ratio = round(float(balance_month)/income_month, 2) #月结余率
income_year = (income_month*12+income_year_bonus+income_year_extra) #年收入
expend_year = (expend_month*12+expend_year_extra) #年支出
balance_year = (income_year-expend_year) #年结余
balance_year_ratio = round(float(balance_year)/income_year, 2) #月结余率
