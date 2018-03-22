# -*- coding: utf-8 -*-

# pylint: disable=E0602

non_invest = [deposit_current, deposit_fixed] #非投资品资产
invest = [funds_money, funds_hybrid, funds_bond, funds_stock, funds_other, invest_bank, invest_stock, invest_national_debt, invest_p2p, invest_insure, invest_metal, invest_other] #投资品资产

complex_fin_assets = deposit_current+deposit_fixed+funds_money+funds_hybrid+funds_bond+funds_stock+funds_other+invest_bank+invest_stock+invest_national_debt+invest_p2p+invest_insure+invest_metal+invest_other #金融资产

fin_assets = sum(non_invest+invest) #金融资产
total_assets = fin_assets+real_estate_value #资产总值
total_debt = consumer_loans+real_estate_loan #总负债
net_assets = total_assets-total_debt #净资产
debt_ratio = round(float(total_debt)/total_assets, 2) #资产负债率
invest_eval = sum([1 if i>0 else 0 for i in invest]) #投资评价
