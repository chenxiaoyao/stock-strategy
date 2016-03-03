# coding=utf-8

# R-001 华宝添益策略

import tushare as ts
import sys
import os
import pandas as pd
import datetime
import numpy as np

def readStockBasics():
    stock_basics_path = os.path.join(dataDir, 'stock-basics.csv')
    if not os.path.exists(stock_basics_path):
        stockBasics_df = ts.get_stock_basics()
        stockBasics_df.to_csv(stock_basics_path, index_label='code')
        return stockBasics_df
    else:
        return pd.read_csv(stock_basics_path, index_col='code')

two_month_ago_date = datetime.datetime.now() + datetime.timedelta(-60)
two_month_ago_date_str = '%4s-%2s-%2s' %(two_month_ago_date.year, two_month_ago_date.month, two_month_ago_date.day)

def isToday(d):
    today = datetime.datetime.now()
    return d.year == today.year and d.month == today.month and d.day == today.day

def readHistoryData(code):
    hist_df = pd.DataFrame()
    code = str(code)
    hist_file_path = os.path.join(dataDir, '%s-hist.csv' %code)
    if os.path.exists(hist_file_path):
        modify_date = datetime.datetime.fromtimestamp(os.path.getmtime(hist_file_path))
        if isToday(modify_date):
            hist_df = pd.read_csv(hist_file_path)
    if hist_df.empty:
        hist_df = ts.get_hist_data(code, start=two_month_ago_date_str)
        hist_df.to_csv(hist_file_path)
    return hist_df

price_df = ts.get_realtime_quotes(['600886', '600674', '000858', '510900', '150176']).set_index('code')
price_df = price_df.rename_axis(mapper= lambda a: int(a), axis=0)

scriptDir = sys.path[0]  # script dir
dataDir = os.path.join(scriptDir, 'cache') #data dir
if not os.path.exists(dataDir):
    os.mkdir(dataDir)
stockBasics_df = readStockBasics()
#merge stock info to stock price DataFrame. Drop column 'name' of sotck basics before merge, because it's duplicated in price_df
price_df = pd.concat([price_df, stockBasics_df.drop('name', 1).loc[np.intersect1d(stockBasics_df.index, price_df.index)]], axis=1)

def calculateGrowth(pre, cur):
    return (float(cur) - float(pre)) / float(pre)

def formatStr(str, len_expect):
    real_len = len(str)
    if real_len >= len_expect:
        return str
    asciiLen = 0
    for ch in str:
        asciiLen = (ord(ch) < 128 and asciiLen + 1 or asciiLen + 2)
    if asciiLen >= len_expect:
        return str
    return str.rjust(real_len + len_expect - asciiLen)

def printStockPrice(price_df):
    iter = price_df.iterrows()
    print '%s%s%s%s%s%s%s' %(formatStr(u'名称', 12), formatStr(u'价格', 9), formatStr(u'最高', 9), \
    formatStr(u'最低', 9), formatStr(u'涨幅', 10), 'PE'.rjust(9), 'PB'.rjust(9))
    for row in iter:
        info = row[1] #Series
        print '%s%9.2f%9.2f%9.2f%9.2f%%%9.2f%9.2f' %(formatStr(info['name'], 12), float(info['price']), \
        float(info['high']), float(info['low']), calculateGrowth(info['pre_close'], info['price']) * 100, float(info['pe']), float(info['pb']))

def calculateTotalValue(code):
    return float(price_df.at[code, 'price']) * price_df.at[code, 'totals'] / 10000

def gtdl_ctny_strategy():
    diff = calculateTotalValue(600886) - calculateTotalValue(600674)
    print u'国投与川投市值差异为：%5.2f亿' %diff
    #雅砻江差值60亿（总估值1500亿），火电80亿
    threshold = 60 + 80
    if diff < threshold:
        print u'差值少于%d，应该持有国投' %threshold
    else:
        print u'差值大于%d，应该持有川投' %threshold

def hgetf_hgb_strategy():
    hgetf_price = price_df.at[510900, 'price']
    hgb_price = price_df.at[150176, 'price']
    ratio = hgb_price / hgetf_price

#last 30 work day average stock price
def calculateAverageClosePrice(code):
    return readHistoryData(code).tail(30).sum(0)['close'] / 30

def print_hgb_hgetf_info(pastRatio, currentRatio, baseStockName, targetStockName):
    print u'过去30个交易日，%s / %s股价比值为%6.3f，当前比值为%6.3f' %(targetStockName, baseStockName, pastRatio, currentRatio)
    growth = calculateGrowth(pastRatio, currentRatio)
    if growth < -0.03:
        print u'比值变化为%6.2f%%，应该换入%s' %(growth * 100, targetStockName)
    else:
        print u'比值变化为%6.2f%%，不用操作' %(growth * 100)

def hgb_hgetf_strategy():
    pastRatio = calculateAverageClosePrice('150176') / calculateAverageClosePrice('510900')
    currentRatio = float(price_df.at[150176, 'price']) / float(price_df.at[510900, 'price'])
    if currentRatio <= pastRatio:
        print_hgb_hgetf_info(pastRatio, currentRatio, u'H股ETF', u'H股B')
    else:
        pastRatio = 1 / pastRatio
        currentRatio = 1 / currentRatio
        print_hgb_hgetf_info(pastRatio, currentRatio, u'H股B', u'H股ETF')

printStockPrice(price_df)
gtdl_ctny_strategy()
hgb_hgetf_strategy()

