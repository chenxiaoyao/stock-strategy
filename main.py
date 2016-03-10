# coding=utf-8

# R-001 华宝添益策略
# 指数交易量

import tushare as ts
import sys
import os
import pandas as pd
import datetime
import numpy as np
import utils

def readStockBasics():
    stock_basics_path = os.path.join(dataDir, 'stock-basics.csv')
    if not os.path.exists(stock_basics_path):
        stockBasics_df = ts.get_stock_basics()
        stockBasics_df.to_csv(stock_basics_path, index_label='code')
        return stockBasics_df
    else:
        return pd.read_csv(stock_basics_path, index_col='code')


dataDir = utils.getDataDir()
stockBasics_df = readStockBasics()

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
        print '%s%9.3f%9.3f%9.3f%9.2f%%%9.2f%9.2f' %(formatStr(info['name'], 12), float(info['price']), \
        float(info['high']), float(info['low']), utils.calculateGrowth(info['pre_close'], info['price']) * 100, float(info['pe']), float(info['pb']))

def main():
    strategyDir = os.path.join(sys.path[0], 'strategy')
    codes=[]
    strategies = []
    for child in os.listdir(strategyDir):
        path = os.path.join(strategyDir, child)
        if os.path.isdir(path):
            if not os.path.exists(os.path.join(path, 'strategy.py')):
                continue
            strategyScript = '.'.join(['strategy', child, 'strategy'])
            module = __import__(strategyScript, {}, {}, ['any'])
            if 'getStockList' in dir(module):
                codes.extend(module.getStockList())
            strategies.append(module)
    codes = ['%06d' %(int(code)) for code in set(codes)]

    global price_df
    price_df = ts.get_realtime_quotes(codes).set_index('code')
    price_df = price_df.rename_axis(mapper= lambda a: int(a), axis=0)

    #merge stock info to stock price DataFrame. Drop column 'name' of sotck basics before merge, because it's duplicated in price_df
    price_df = pd.concat([price_df, stockBasics_df.drop('name', 1).loc[np.intersect1d(stockBasics_df.index, price_df.index)]], axis=1)

    printStockPrice(price_df)
    for s in strategies:
        print utils.getSeperateLine()
        s.run(price_df)

if __name__ == '__main__':
    main()

