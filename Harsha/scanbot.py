# Global imports
from Bittrex import *
from coinClass import *

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
	if res['MarketName'][0:3] == 'BTC' and float(res['BaseVolume']) >= 20:
	    coinList.append(res['MarketName'])
        count = count +1

# Create Databases to store the jsons poll every 60 sec and store max of 6 hrs
for coin in coinList:
    market = '{0}{1}'.format(coin, '_col')
    coinCollection[market] = collections.deque(360*[0],360)

#for each item in the coinlist start a thread and open the file and read values of individual coins
for coin in coinList:
	thread = coinThread(coin,coinCollection['{0}{1}'.format(coin, '_col')])
	thread.start()

###########################################################
# Testing
###########################################################

#Test for a coin
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