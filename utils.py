# coding=utf-8
import tushare as ts
import pandas as pd
import os, sys
import datetime

def getSeperateLine():
    return '============================================================'

#private
#judge the day is today
def isToday(d):
    today = datetime.datetime.now()
    return d.year == today.year and d.month == today.month and d.day == today.day

#private
def readHistoryData(code):
    hist_df = pd.DataFrame()
    code = '%06d' %(int(code))
    dataDir = getDataDir()
    hist_file_path = os.path.join(dataDir, '%s-hist.csv' %code)
    if os.path.exists(hist_file_path):
        modify_date = datetime.datetime.fromtimestamp(os.path.getmtime(hist_file_path))
        if isToday(modify_date):
            hist_df = pd.read_csv(hist_file_path)
    if hist_df.empty:
        two_month_ago_date = datetime.datetime.now() + datetime.timedelta(-60)
        two_month_ago_date_str = '%4s-%2s-%2s' %(two_month_ago_date.year, two_month_ago_date.month, two_month_ago_date.day)
        hist_df = ts.get_hist_data(code, start=two_month_ago_date_str)
        hist_df.to_csv(hist_file_path)
    return hist_df

def getDataDir():
    scriptDir = sys.path[0]  # script dir
    dataDir = os.path.join(scriptDir, 'cache') #data dir
    if not os.path.exists(dataDir):
        os.mkdir(dataDir)
    return dataDir

def calculateGrowth(pre, cur):
    return (float(cur) - float(pre)) / float(pre)


#last 30 work day average stock price
def calculateAverageClosePrice(code):
    return readHistoryData(code).tail(30).sum(0)['close'] / 30

#计息stock的总市值，单位亿
def calculateTotalValue(stock_df, code):
    return float(stock_df.at[code, 'price']) * stock_df.at[code, 'totals'] / 10000