# Global imports
from bittrex_v2 import Bittrex
from coinClass import *
import json
import collections
import time

###########################################################
# Scan Bot
###########################################################
# List of all the coins
coinList = []

# Global collection for storing all the data for coins
coinCollection = {}

# poll the Bittrex for all the possible currencies BTCXXX
currencySummary = testapi.get_market_summaries()

# Get just the BTC currencies and which are active
count = 0
for res in currencySummary['result']:
	if (res['Summary']['MarketName'][0:3] == 'BTC' and float(res['Summary']['BaseVolume']) >= 20):
		coinList.append(res['Summary']['MarketName'])
		count = count + 1

# Create Databases to store the jsons poll every 60 sec and store max of 10 hrs
#coinList = ['BTC-XRP']
for coin in coinList:
    market = '{0}{1}'.format(coin, '_col')
    coinCollection[market] = collections.deque(6000*[0],6000)

#for each item in the coinlist start a thread and open the file and read values of individual coins
for coin in coinList:
	thread = coinThread(coin,coinCollection['{0}{1}'.format(coin, '_col')])
	thread.start()

###########################################################
# Telegram Thread Start
###########################################################

thread = telegramThread()
thread.start()

###########################################################
# Testing
###########################################################

#Test for a coin
'''
Analyze=['BTC-XLM']

try:
    while (True):
        time.sleep(53)
        for x in Analyze:
            analyze = coinAnalyze(x,coinCollection)
            analyze.change_1min()
            analyze.change_2min()
            analyze.change_5min()
            analyze.change_30min()
            analyze.change_60min()

except KeyboardInterrupt:
    print "ctrl+ c pressed"
    exit(0)
'''

###########################################################
# Testing for continous mean increases
###########################################################
#coinList = ['BTC-XRP']
try:
    while (True):
        time.sleep(47)
        for coin in coinList:
            analyze = coinAnalyze(coin,coinCollection)
            analyze.ascendingMean(1)
            analyze.ascendingMean(5)
            analyze.ascendingMean(10)
            analyze.ascendingMean(30)
            analyze.ascendingMean(60)
            analyze.ascendingMean(120)
            analyze.ascendingMean(180)
            analyze.ascendingMean(600)
            analyze.ascendingMean(1440)
            
except KeyboardInterrupt:
	print ("ctrl+ c pressed")
	exit(0)
    
