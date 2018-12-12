# -*- coding: utf-8 -*-
"""
Web-scraping of NIFTY 50 stock data from moneycontrol.com

Created on Sat Dec  8 16:18:24 2018

@author: PareshBhatia
"""
#import required libraries
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt

#base url from where we will get list of NIFTY50 stocks
nifty_url = "https://www.moneycontrol.com/stocks/marketstats/indexcomp.php?optex=NSE&opttopic=indexcomp&index=9"

#initialize empty list for storing stock names and their moneycontrol urls
stocks = []
stock_url = []

#get data from page
response = requests.get(nifty_url)
soup = BeautifulSoup(response.text,"html.parser")
#below will extract <a> tags containing moneycontrol links and all the stock names
stocklist = soup.find_all('a',href=re.compile('stockpricequote'),class_='bl_12')

#store all stock names in stocks and urls in stock_url
for stock in stocklist:
    stocks.append(stock.find("b").get_text())
    stock_url.append(stock['href'])
#this is homepage url of moneycontrol. We will add it in stocks url to get full url of a stock    
base_url = "https://www.moneycontrol.com"

#create empty dataframe to store stock details.
stock_info = pd.DataFrame()
    
#initialize an empty list to store stock details
current_price = []
todays_updown = []
up_down = []
prev_close =[]
open_price = []
todays_low = []
todays_high = []
f52week_low = []
f52week_high = []

#iterate over stock urls of differnt stocks in nifty and extract details
for stock,url in list(zip(stocks,stock_url)):
    response_stock = requests.get(base_url+url)
    soup1 = BeautifulSoup(response_stock.text,"html.parser")
    #print(base_url+stock_url[0])
    nse_details =soup1.find("div",id="content_nse")
    current_price.append(nse_details.find("span",id="Nse_Prc_tick").find_next("strong").get_text())
    todays_updown.append(nse_details.find("div",id="n_changetext").find_next("strong").get_text())
    up_down.append(nse_details.find("div",id="n_changetext").get_text().split(' ')[2].
                   replace('(','').replace(')','').replace('%','').replace('+',''))
    prev_close.append(nse_details.find("div",id="n_prevclose").find_next("strong").get_text())
    open_price.append(nse_details.find("div",id="n_open").find_next("strong").get_text())
    todays_low.append(nse_details.find("span",id="n_low_sh").get_text())
    todays_high.append(nse_details.find("span",id="n_high_sh").get_text())
    f52week_low.append(nse_details.find("span",id="n_52low").get_text())
    f52week_high.append(nse_details.find("span",id="n_52high").get_text())

#assign stock details list to dataframe columns
stock_info['stock'] = stocks
stock_info['current_price'] =current_price
stock_info['todays_up/down'] = todays_updown
stock_info['up/down%'] = up_down
stock_info['prev_close'] = prev_close
stock_info['open_price'] = open_price
stock_info['todays_low'] = todays_low
stock_info['todays_high'] = todays_high
stock_info['52week_low'] = f52week_low
stock_info['52week_high'] = f52week_high
stock_info = stock_info.set_index('stock')   
numeric_cols =[ cols for cols in stock_info.columns if cols not in ['stock'] ]

for col in numeric_cols:
    stock_info[col] = pd.to_numeric(stock_info[col],errors='coerce')


fig, ax =plt.subplots(1,2,figsize=(20,8))
top_gainers = stock_info['up/down%'].sort_values(ascending=False)[:5]
sns.barplot(x=top_gainers.index,y=top_gainers.values,ax=ax[0]).set_title('Top Gainers')

top_loosers = stock_info['up/down%'].sort_values()[:5]
sns.barplot(y=top_loosers.index,x=top_loosers.values,ax=ax[1]).set_title('Top Loosers')
fig.suptitle(dt.date.today())
fig.savefig('TopGainers&Loosers1.jpeg')
    