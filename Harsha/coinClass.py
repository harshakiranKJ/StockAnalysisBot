from Bittrex import *
import numpy as np
import telebot
import threading
import time
import pandas as pd

###########################################################
# Global Initializations
###########################################################
#generate new API key/secret from Bittrex and put them here
bkey = ""
bskey= ""

# put in the telegram bot token from @BotFather
TOKEN = "477814364:AAGWlwRFp9LR77M8QmByyrhUeVBrSH4KW7w"

#initialize the telegram BOT and Bittrex
testapi = Bittrex(api_key=bkey, api_secret=bskey)
bot = telebot.TeleBot(TOKEN)

records = 0

###########################################################
# Global Analysis results and thread to clear
###########################################################

collectionResults = {"avg1res":[],"avg5res":[],"avg10res":[],"avg30res":[],"avg60res":[],"avg120res":[],"avg180res":[],"avg600res":[],"avg1440res":[]}

###########################################################
# Telegram Thread
###########################################################

class telegramThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print ("starting telegram thread")

        @bot.message_handler(commands=['avg1'])
        def send_welcome(message):
            bot.reply_to(message, " ".join(str(x) for x in collectionResults['avg1res']))

        @bot.message_handler(commands=['avg5'])
        def send_welcome(message):
            bot.reply_to(message, " ".join(str(x) for x in collectionResults['avg5res']))

        @bot.message_handler(commands=['avg10'])
        def send_welcome(message):
            bot.reply_to(message, " ".join(str(x) for x in collectionResults['avg10res']))

        @bot.message_handler(commands=['avg30'])
        def send_welcome(message):
            bot.reply_to(message, " ".join(str(x) for x in collectionResults['avg30res']))

        @bot.message_handler(commands=['avg60'])
        def send_welcome(message):
            bot.reply_to(message, " ".join(str(x) for x in collectionResults['avg60res']))

        @bot.message_handler(commands=['avg120'])
        def send_welcome(message):
            bot.reply_to(message, " ".join(str(x) for x in collectionResults['avg120res']))

        @bot.message_handler(commands=['avg180'])
        def send_welcome(message):
            bot.reply_to(message, " ".join(str(x) for x in collectionResults['avg180res']))

        @bot.message_handler(commands=['avg600'])
        def send_welcome(message):
            bot.reply_to(message, " ".join(str(x) for x in collectionResults['avg600res']))

        @bot.message_handler(commands=['avg1440'])
        def send_welcome(message):
            bot.reply_to(message, " ".join(str(x) for x in collectionResults['avg1440res']))

        @bot.message_handler(commands=['rec'])
        def send_welcome(message):
            bot.reply_to(message, records)

        @bot.message_handler(func=lambda message: True)
        def echo_all(message):
            bot.reply_to(message, "Please check commands Eg: avg[1, 5,10,30,60,120,180,600,1440]")

        while (True):
    
            try:
                bot.polling(none_stop=True)

            except Exception as e:
                time.sleep(15)



###########################################################
# Thread Class to get the data contiously every minute
# @name : name of the coin 
# @db   : a Fixed length FIFO deque storing 6 hrs of data
###########################################################

class coinThread (threading.Thread):
    
    tcounter = 0

    def __init__(self, name,db):
      threading.Thread.__init__(self)
      self.name = name
      self.db = db

    def run(self):
        try:
            #print ("starting Collection thread")
            while (True):
                # Create local storage for recursive data
                localCollection = []

                start = time.time()
                stop = start + 33     # 47 seconds for gathering data
                scounter = 0
                fcounter = 0
                while (time.time() < stop):
                    #print ("Thread COLLECTION START Time: " + str(time.ctime()))
                    data = testapi.get_market_summary(self.name)
                    
                    if (data['success'] == True):
                        localCollection.append(data['result'])
                        scounter = scounter +1
                    else:
                        fcounter = fcounter +1
                    
                    #print ("coin : " + self.name)
                    #print ("now time : " +str(time.time()))
                    #print ("stop time: " + str(stop))
                    time.sleep(10)

                #print ("scounter : "  str(scounter))
                #print "fcounter : " + str(fcounter)

                #calculate average of each value based on the counter
                coldata = pd.DataFrame.from_dict(localCollection) 
                coldata = coldata.mean()
                coldata = coldata.to_dict()

                # push the mean value to the database
                self.db.appendleft(coldata)
                #print "Thread COLLECTION STOP Time: " + str(time.ctime())
                deltasleep = time.time() - start
                self.tcounter = self.tcounter + 1
                print ("database increment: " + str(self.tcounter))
                records = self.tcounter
                print ("number of records:" + str())
                time.sleep(abs(60 - deltasleep))
        except KeyboardInterrupt:
            print ("ctrl+ c pressed")
            threading.Thread._Thread_stop()


###########################################################
# Global Helper Functions
#
#
###########################################################

# run multithreads for the count of number of currencies
def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (current - previous)
    except ZeroDivisionError:
        return 0

###########################################################
# Analysis Class to get the data contiously every minute
# @coin : name of the coin 
# @db   : a Fixed length FIFO deque storing 6 hrs of data
###########################################################
class coinAnalyze():
    # static variable for storing previous values
    calChangeDict = {"change1min":{"previous":0},"change2min":{"previous":0},"change5min":{"previous":0},"change30min":{"previous":0},"change60min":{"previous":0}}

    def __init__(self,coin,coinCollection):
        self.coin = coin
        self.coinCollection = coinCollection

    def change_1min(self):
        self.findChange(1)

    def change_5min(self):
        self.findChange(5)
        
    def change_5min(self):
        self.findChange(10)
    
    def change_30min(self):
        self.findChange(30)

    def change_60min(self):
        self.findChange(60)
        
    def change_60min(self):
        self.findChange(120)
        
    def change_60min(self):
        self.findChange(180)
        
    def change_60min(self):
        self.findChange(600)
        
    def change_60min(self):
        self.findChange(1440)
    
    def findChange(self,duration):
        try:
            
            #format and fetch Data
            market = '{0}{1}'.format(self.coin, '_col')             # Get the coin (BTC-XRP)
            val = self.coinCollection[market]                       # Get the required database
            data = [elem for elem in val if elem !=0]               # format to remove zeros
            if (len(data) <= duration):                             # return if not enough data is available
                return
            coldata = pd.DataFrame.from_dict(data)                  # Store the data in a python pandas dataframe
            changename = 'change{0}min'.format(duration)            # calculate the collection string

            #calculate change
            prev_val = self.calChangeDict[changename]['previous']   # prev ?
            curr_val = coldata['BaseVolume'][duration -1]           # curr ?
            self.calChangeDict[changename]['previous'] = curr_val   # prev is current
            change = get_change(curr_val,prev_val)                  # change ?

            # Report if % change is more than 2BTC
            if change > 2:
                bot.send_message(chat_id=TG_ID, text="<b>BITTREX: </b>"+' '.join(self.coin + " volume increased by" +  str(change) + " BTC in : " + str(duration) + "minutes"), parse_mode=telegram.ParseMode.HTML)
                print ("Coin: "+ self.coin + "BTC volume increased by"+ str(change)+" BTC in : " + str(duration) + "minutes")
            if change < -2:
                bot.send_message(chat_id=TG_ID, text="<b>BITTREX: </b>"+' '.join(self.coin + " volume decreased by" +  str(change) + " BTC in : " + str(duration) + "minutes"), parse_mode=telegram.ParseMode.HTML)

        except KeyboardInterrupt:
                print ("ctrl+ c pressed")
                exit(0)

    def ascendingMean(self,duration):
        try:

            print ("Thread ANALYZE start Time: " + str(time.ctime()))

            #format and fetch Data
            market = '{0}{1}'.format(self.coin, '_col')             # Get the coin (BTC-XRP)
            val = self.coinCollection[market]                       # Get the required database
            data = [elem for elem in val if elem !=0]               # format to remove zeros
            print (data)
            print ("Data in Analysis threads" + str(len(data)))
            if (len(data) < 3 * duration):                             # return if not enough data is available
                #print "Not enough data!!" + str(duration)
                return
            coldata = pd.DataFrame.from_dict(data)                  # Store the data in a python pandas dataframe

            # Calculate ascending means from start till the duration mentioned
            mean1 = np.mean(coldata['Last'][0:duration])
            mean2 = np.mean(coldata['Last'][duration:2*duration])
            mean3 = np.mean(coldata['Last'][2*duration:3*duration])

            #print "mean1: " + str(mean1)
            #print "mean1: " + str(mean1)
            #print "mean1: " + str(mean1)
            #print val

            # clear the previous data so it wont accumilate
            #del collectionResults['avg{0}res'.format(duration)][:]

            if ((mean1 > mean2) and (mean2 > mean3)):
                if self.coin in collectionResults['avg{0}res'.format(duration)]:
                    return
                else:
                    collectionResults['avg{0}res'.format(duration)].append(self.coin)

        except KeyboardInterrupt:
                print ("ctrl+ c pressed")
                exit(0)



###########################################################
# Generic helper functions
#  
# 
###########################################################
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def do_print(value,num):
    if num ==1:
        print ("\n\n\n***********************",value,"***************************\n")
    if num == 2:
        print ("\n***********************",value,"***************************\n\n")
    if num==3:
        if value['success'] == True:
            print (bcolors.OKGREEN + "SUCCESS" + bcolors.ENDC)
            print (bcolors.OKGREEN + str(value) + bcolors.ENDC)
        else:
            print (bcolors.FAIL + "FAILED" + bcolors.ENDC)
            print (bcolors.FAIL + str(value) + bcolors.ENDC)

# run multithreads for the count of number of currencies
def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (current - previous)
    except ZeroDivisionError:
        return 0
