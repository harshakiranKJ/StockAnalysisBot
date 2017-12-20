from Bittrex import *


###########################################################
# Global Initializations
###########################################################
#generate new API key/secret from Bittrex and put them here
bkey = ""
bskey= ""

# put in your telegram chat id from @get_id_bot
TG_ID = ""

# put in the telegram bot token from @BotFather
TG_BOT_TOKEN = ""


#initialize the telegram BOT and Bittrex
testapi = Bittrex(bkey, bskey)
bot = telegram.Bot(token=TG_BOT_TOKEN)


###########################################################
# Thread Class to get the data contiously every minute
# @name : name of the coin 
# @db   : a Fixed length FIFO deque storing 6 hrs of data
###########################################################

class coinThread (threading.Thread):
   def __init__(self, name,db):
      threading.Thread.__init__(self)
      self.name = name
      self.db = db

   def run(self):
        try:
            while (True):
                coinData = testapi.get_market_summary(self.name)
                self.db.appendleft(coinData['result'][0])
                time.sleep(60)
        except KeyboardInterrupt:
            print "ctrl+ c pressed"
            threading.Thread._Thread_stop()



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

    def change_2min(self):
        self.findChange(2)

    def change_5min(self):
        self.findChange(5)
    
    def change_30min(self):
        self.findChange(30)

    def change_60min(self):
        self.findChange(60)
    
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
                print "Coin: "+ self.coin + "BTC volume increased by"+ str(change)+" BTC in : " + str(duration) + "minutes"
            if change < -2:
                bot.send_message(chat_id=TG_ID, text="<b>BITTREX: </b>"+' '.join(self.coin + " volume decreased by" +  str(change) + " BTC in : " + str(duration) + "minutes"), parse_mode=telegram.ParseMode.HTML)

        except KeyboardInterrupt:
                print "ctrl+ c pressed"
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
        print "\n\n\n***********************",value,"***************************\n"
    if num == 2:
        print "\n***********************",value,"***************************\n\n"
    if num==3:
        if value['success'] == True:
            print bcolors.OKGREEN + "SUCCESS" + bcolors.ENDC
            print bcolors.OKGREEN + str(value) + bcolors.ENDC
        else:
            print bcolors.FAIL + "FAILED" + bcolors.ENDC
            print bcolors.FAIL + str(value) + bcolors.ENDC

# run multithreads for the count of number of currencies
def get_change(current, previous):
    if current == previous:
        return 0
    try:
        return (current - previous)
    except ZeroDivisionError:
        return 0