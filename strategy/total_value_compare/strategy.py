#coding=utf-8

import strategy_data as data
import utils

def getStockList():
    all = []
    for pair in data.info:
        all.extend(pair[0 : 2])
    return all

def run(price_df):
    global df
    df = price_df
    for pair in data.info:
        code1 = pair[0]
        code2 = pair[1]
        threshold = pair[2]
        name1 = df.at[code1, 'name']
        name2 = df.at[code2, 'name']
        diff = utils.calculateTotalValue(df, code1) - utils.calculateTotalValue(df, code2)

        print u'%s与%s市值差异为：%5.2f亿' %(name1, name2, diff)
        if diff < threshold:
            print u'差值小于%d，应该持有%s' %(threshold, name1)
        else:
            print u'差值大于%d，应该持有%s' %(threshold, name2)
