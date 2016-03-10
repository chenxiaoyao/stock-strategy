#coding=utf-8

import strategy_data as data
import utils

def getStockList():
    return list(sum(data.stock_pair, ()))

def print_hgb_hgetf_info(pastRatio, currentRatio, baseStockName, targetStockName):
    print u'过去30个交易日，%s / %s股价比值为%6.3f，当前比值为%6.3f' %(targetStockName, baseStockName, pastRatio, currentRatio)
    growth = utils.calculateGrowth(pastRatio, currentRatio)
    if growth < -0.03:
        print u'比值变化为%6.2f%%，应该换入%s' %(growth * 100, targetStockName)
    else:
        print u'比值变化为%6.2f%%，不用操作' %(growth * 100)

def compareStockPrice(code1, code2):
    global df
    name1 = df.at[code1, 'name']
    name2 = df.at[code2, 'name']
    pastRatio = utils.calculateAverageClosePrice(code1) / utils.calculateAverageClosePrice(code2)
    currentRatio = float(df.at[code1, 'price']) / float(df.at[code2, 'price'])
    if currentRatio <= pastRatio:
        print_hgb_hgetf_info(pastRatio, currentRatio, name2, name1)
    else:
        pastRatio = 1 / pastRatio
        currentRatio = 1 / currentRatio
        print_hgb_hgetf_info(pastRatio, currentRatio, name1, name2)

def run(price_df):
    global df
    df = price_df
    for pair in data.stock_pair:
        compareStockPrice(pair[0], pair[1])
