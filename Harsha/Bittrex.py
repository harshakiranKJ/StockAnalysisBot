# Bitrex APIS

import imp, pip
def install(package):
	pip.main(["install", package])
	
depends = ['requests', 'python-telegram-bot','pandas']
for i in depends:
	try:
		imp.find_module(i)
	except ImportError:
		print "The '"+i+"' package is not installed. Attempting to install..."
		install(i)


import threading
import os
# import ssl
import sys
import telegram
import time
import json
import time, datetime
import datetime
import calendar
import hmac, hashlib
import httplib
import requests
import pandas as tName
import collections
import signal
import pandas as pd

try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import Request, urlopen, URLError, HTTPError
    from urllib import urlencode

# BITTREX APIS
BUY_ORDERBOOK = 'buy'
SELL_ORDERBOOK = 'sell'
BOTH_ORDERBOOK = 'both'

PUBLIC_SET = ['getmarkets', 'getcurrencies', 'getticker', 'getmarketsummary', 'getmarketsummaries', 'getorderbook',
          'getmarkethistory']

MARKET_SET = ['getopenorders', 'cancel', 'sellmarket', 'selllimit', 'buymarket', 'buylimit']

ACCOUNT_SET = ['getbalances', 'getbalance', 'getdepositaddress', 'withdraw', 'getorder', 'getorderhistory', 'getwithdrawalhistory', 'getdeposithistory']


class Bittrex(object):

    def __init__(self, api_key, api_secret):
        self.api_key = str(api_key) if api_key is not None else ''
        self.api_secret = str(api_secret) if api_secret is not None else ''
        self.public_set = set(PUBLIC_SET)
        self.market_set = set(MARKET_SET)
        self.account_set = set(ACCOUNT_SET)

    def api_query(self, method, options=None):
        if not options:
            options = {}
        nonce = str(int(time.time() * 1000))
        base_url = 'https://bittrex.com/api/v1.1/%s/'
        request_url = ''

        if method in self.public_set:
            request_url = (base_url % 'public') + method + '?'
        elif method in self.market_set:
            request_url = (base_url % 'market') + method + '?apikey=' + self.api_key + "&nonce=" + nonce + '&'
        elif method in self.account_set:
            request_url = (base_url % 'account') + method + '?apikey=' + self.api_key + "&nonce=" + nonce + '&'
        #print(options)
        request_url += urlencode(options)

        signature = hmac.new(self.api_secret, request_url, hashlib.sha512).hexdigest()

        headers = {"apisign": signature}

        try:
            ret = requests.get(request_url, headers=headers)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
            return {}
#        print dir(ret)
        if ret.ok:
            return ret.json()
        else:
            return {'success':False}

#       print ret.text, ret.ok, ret.reason, ret.status_code

    def get_markets(self):
        return self.api_query('getmarkets')

    def get_currencies(self):
        return self.api_query('getcurrencies')

    def get_ticker(self, market):
         return self.api_query('getticker', {'market': market})

    def get_market_summaries(self):
        return self.api_query('getmarketsummaries')

    def get_market_summary(self, market):
        return self.api_query('getmarketsummary', {'market': market})
		
    def get_orderbook(self, market, depth_type, depth=20):
        return self.api_query('getorderbook', {'market': market, 'type': depth_type, 'depth': depth})

    def get_market_history(self, market, count):
        return self.api_query('getmarkethistory', {'market': market, 'count': count})

    def buy_market(self, market, quantity, rate):
        return self.api_query('buymarket', {'market': market, 'quantity': quantity, 'rate': rate})

    def buy_limit(self, market, quantity, rate):
        return self.api_query('buylimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def sell_market(self, market, quantity, rate):
        return self.api_query('sellmarket', {'market': market, 'quantity': quantity, 'rate': rate})

    def sell_limit(self, market, quantity, rate):
       return self.api_query('selllimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def cancel(self, uuid):
       return self.api_query('cancel', {'uuid': uuid})

    def get_open_orders(self, market):
        return self.api_query('getopenorders', {'market': market})

    def get_open_orders(self):
        return self.api_query('getopenorders')

    def get_balances(self):
       return self.api_query('getbalances', {})

    def get_balance(self, currency):
        return self.api_query('getbalance', {'currency': currency})

    def get_deposit_address(self, currency):
       return self.api_query('getdepositaddress', {'currency': currency})

    def get_order(self, uuid):
       return self.api_query('getorder', {'uuid': uuid})

    def get_deposit_history(self, currency=""):
        if currency == "":
            return self.api_query('getdeposithistory')
        else:
            return self.api_query('getdeposithistory', {"currency": currency})

    def get_withdrawal_history(self, currency=""):
        if currency == "":
            return self.api_query('getwithdrawalhistory')
        else:
            return self.api_query('getwithdrawalhistory', {"currency": currency})

    def get_order_history(self, market = ""):
        if market == "":
            return self.api_query('getorderhistory')
        else:
            return self.api_query('getorderhistory', {"market": market})




