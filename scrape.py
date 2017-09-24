from functions import *


import sys, urllib2, shutil
sys.path.append("/usr/local/lib/python2.7/site-packages")
import simplejson
import json
import datetime
import ast
from lxml import html
from lxml import etree
import requests
from decimal import Decimal

from time import gmtime, strftime




# *************************************************************
# Get the bitcoin value the the number of days previous
# eg A value of 7 will return the value of a bitcoin 7 days ago
# *************************************************************
def getBitcoinValue(numberOfDays):
    if(numberOfDays > 0):
        today = datetime.datetime.today()
        todayStr = str(today.strftime('%Y-%m-%d'))
        start_date = today - datetime.timedelta(days=numberOfDays)
        start_dateStr = str(start_date.strftime('%Y-%m-%d'))

        url = "http://api.coindesk.com/v1/bpi/historical/close.json?currency=EUR&start="+start_dateStr+"&end="+todayStr

        response = urllib2.urlopen(url)
        data = simplejson.load(response)

        return data['bpi'][start_dateStr]
    else:
        # Get the current price in EUR
        url = "http://api.coindesk.com/v1/bpi/currentprice.json"

        response = urllib2.urlopen(url)
        data = simplejson.load(response)

        return data['bpi']['EUR']['rate']




# *************************************************************
# Get the basic JSON description of the market
# (NO STATS - Only contains market name and trading currency)
# *************************************************************
def getMarket():
    response = urllib2.urlopen("https://www.coinexchange.io/api/v1/getmarkets")
    data = simplejson.load(response)
    return data["result"]
def getMarketDetails():
    response = urllib2.urlopen("https://www.coinexchange.io/api/v1/getmarketsummaries")
    data = simplejson.load(response)
    return data["result"]


def getBitcoinTradingMarket():
    one = getMarket()
    two = getMarketDetails()
    for currency1 in one:
        oneID = currency1["MarketID"]
        for currency2 in two:
            if currency2["MarketID"] == oneID:
                for details in currency2:
                    currency1[details] = currency2[details]
                break
    #remove inactive and non BTC currencies
    market = []
    for currency in one:
        if currency["BaseCurrencyCode"]=="BTC" and currency["Active"]==True:
            market.append(currency)

    return market



def getCurrencyFromMarket(market,currencyCode):
    for currency in market:
        if currency["MarketAssetCode"]==currencyCode:
            return currency


# Retrive an array of all MarketIDs listed on the bitcoin market and save to a .csv
def getCurrencyCodes():
    market = getBitcoinTradingMarket()
    result = []
    for currency in market:
        result.append(currency["MarketID"])
    return result


def getCurrencyCode(market, marketID):
    for currency in market:
        if(currency["MarketID"] == marketID):
            return currency["MarketAssetCode"]
    return ''

def getCurrenciesAtLowestValue():
    market = getBitcoinTradingMarket()
    result = []
    for currency in market:
        if currency["LastPrice"] == "0.00000001":
            result.append(currency["MarketAssetCode"])
    return result

def getCurrencyDetail(marketID,detail):
    market = getBitcoinTradingMarket()
    for currency in market:
        if currency["MarketID"] == marketID:
            return currency[detail]



def getNewCurrencies():
    market = getBitcoinTradingMarket()

    root='data'
    oldCurrencies = [os.path.splitext(f)[0] for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
    #print oldCurrencies

    newCurrencies = []
    for currency in market:
        if currency["MarketAssetCode"] not in oldCurrencies:
            #print currency
            addNewCurrencyToDB(currency)
            newCurrencies.append(currency)
    return newCurrencies











def getCurrenciesNowTradingAtOneSat():
    ret = []
    dbFilenames = getDBFilenames()
    for filename in dbFilenames:
        currency = getDBEntry(filename)
        if currency != -1:
            sys.stdout.write('%s \r' % ("           ",))
            sys.stdout.flush()
            sys.stdout.write('%s \r' % (currency["MarketAssetCode"],))
            sys.stdout.flush()

            lastAverageTradeVal = currency["Data"][-1]
            if currency["Data"][-1]["LastPrice"] == "0.00000001" and currency["Data"][-2]["LastPrice"] != "0.00000001":
                ret.append(currency["MarketAssetCode"])
                print currency["MarketAssetCode"] + " - LastPrice=" + currency["Data"][-1]["LastPrice"] + " Second last LastPrice=" + currency["Data"][-2]["LastPrice"]
    return ret





# *************************************************************
# Mining functions
# *************************************************************

#def getDB():
 #   root='data'
 #   filenames = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
    #print filenames
 #   currencies = []
 #   for filename in filenames:
 #   	try:
 #           with open("data/"+filename) as data_file:
 #               data = json.load(data_file)
 #               currencies.append(data)
 #       except Exception, e:
 #           print "Err: could not load json data from file:" + filename + " - " + str(e)
            #return -1
        
 #   return currencies
#def getDBLen():
#    root='data'
#	filenames = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
#	return len(filenames)
#def getDBIndex(index):
#	root='data'
#	filenames = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
#	i = 0
#	for filename in filenames:
#		if i == index:
#			try:
#				with open("data/"+filename) as data_file:
#					data = json.load(data_file)
#					return data
#			except Exception, e:
#				print "Err: could not load json data from file:" + filename + " - " + str(e)
 #               return -1
#		i=i+1
#	print "Err: index out of bounds: " + str(index)
#	return -1    
def getDBFilenames():
    root='data'
    filenames = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]
    return filenames
def getDBEntry(filename):
    root='data'
    try:
        with open("data/"+filename) as data_file:
            data = json.load(data_file)
            return data
    except Exception, e:
        print "Err: could not load json data from file:" + filename + " - " + str(e)
        print "Reverting to bkup.."
        try:
            with open("data/"+filename) as data_file:
                data = json.load(data_file)
                return data
        except Exception, e:
            print "Failed to load bkup file! - " + str(e)

    return -1    

def updateDB(newCurrencies):
    bitcoinMarket = getBitcoinTradingMarket()
    dbEntries = getDBFilenames()

    for filename in dbEntries:
    #db = getDB()
    #for currency in db:
        currency = getDBEntry(filename)
        if currency != -1:
            update = True
            if len(newCurrencies) > 0:
                for newCurrency in newCurrencies:
                    if currency["MarketAssetCode"] == newCurrency["MarketAssetCode"]:
                        update = False
                        break
            if update:
                updateCurrencyInDB(currency["MarketAssetCode"],bitcoinMarket)
    

def getCurrencyFromDB(currencyCode):
    filename = "data/"+currencyCode+".json"
    with open(filename) as data_file:
        currency = json.load(data_file)
    if currency["MarketAssetCode"] == currencyCode:
        return currency
    else:
        return "ERR: Currency Missmatch\nTried to find:"+currencyCode+"\nFound:"+currency["MarketAssetCode"]+" instead!"
def writeCurrencyDataToDB(newData, currencyCode):
    filename = "data/"+currencyCode+".json"
    with open(filename, 'w') as f:
        f.write(json.dumps(newData))
#def updateCurrencyInDB(currencyCode):



#def updateInfoLinks(currencyCode):

def addNewCurrencyToDB(currencyMarketData):

    #restructure the data for multiple sample data
    newCurrency = {}
    newCurrency["MarketAssetCode"] = currencyMarketData["MarketAssetCode"]
    newCurrency["MarketAssetID"] = currencyMarketData["MarketAssetID"]
    newCurrency["MarketAssetName"] = currencyMarketData["MarketAssetName"]
    newCurrency["BaseCurrencyCode"] = currencyMarketData["BaseCurrencyCode"]


    date = strftime("%d-%m-%Y %H:%M:%S", gmtime())
    newCurrency["Data"] = []
    details = {}
    details["Date"] = date
    for detail in currencyMarketData:
        #print detail
        if detail != "MarketAssetCode" and detail != "BaseCurrencyCode" and detail != "MarketAssetID" and detail != "BaseCurrency" and detail != "BaseCurrencyID" and detail != "MarketAssetName":
            details[detail] = currencyMarketData[detail]


    url = "https://www.coinexchange.io/market/"+currencyMarketData["MarketAssetCode"]+"/BTC"
    source = requests.get(url).content
    details["Trades"] = getRecentMarketTrades(newCurrency["MarketAssetCode"],source)
    details["AverageTradeValue"] = getAverageTradeValue(details["Trades"])
    details["BuyOrders"] = getBuyOrders(newCurrency["MarketAssetCode"],source)
    details["SellOrders"] = getSellOrders(newCurrency["MarketAssetCode"],source)

    newCurrency["Data"].append(details)

    filename = "data/" + newCurrency["MarketAssetCode"] + ".json"

    with open(filename, 'w') as outfile:
        json.dump(newCurrency, outfile)


def updateCurrencyInDB(currencyCode, bitcoinMarket):
    #print currencyCode

    marketData = ""
    for currency in bitcoinMarket:
        if currency["MarketAssetCode"] == currencyCode:
            marketData = currency
    if marketData == "":
        print "ERR: currency data not found in bitcoinMarket\n- (updateCurrencyInDB) Could not find " + currencyCode + "\nDeleting from DB.."
        os.remove("data/"+currencyCode+".json")
        return

    filename = "data/" + currencyCode + ".json"
    
    with open(filename) as data_file:
            currency = json.load(data_file)


    date = strftime("%d-%m-%Y %H:%M:%S", gmtime())
    details = {}
    details["Date"] = date

    # add the relevant market data to details
    for marketDetail in marketData:
        if marketDetail != "MarketAssetCode" and marketDetail != "BaseCurrencyCode" and marketDetail != "MarketAssetID" and marketDetail != "BaseCurrency" and marketDetail != "BaseCurrencyID" and marketDetail != "MarketAssetName":
            details[marketDetail] = marketData[marketDetail]


    url = "https://www.coinexchange.io/market/"+currencyCode+"/BTC"
    source = requests.get(url).content
    details["Trades"] = getNewRecentMarketTrades(currency["MarketAssetCode"],source)
    details["AverageTradeValue"] = getAverageTradeValue(details["Trades"])
    details["BuyOrders"] = getBuyOrders(currency["MarketAssetCode"],source)
    details["SellOrders"] = getSellOrders(currency["MarketAssetCode"],source)

    currency["Data"].append(details)

    filename = "data/" + currencyCode + ".json"
    #print filename
    #print currency
    #print newCurrency

    # create backup of the file
    shutil.copy(filename, filename+".bk")
    with open(filename, 'w') as outfile:
        json.dump(currency, outfile)
    # the write completed successfully - delete the bkup
    os.remove(filename+".bk")

    sys.stdout.write('%s \r' % ("           ",))
    sys.stdout.flush()
    sys.stdout.write('%s \r' % (currencyCode,))
    sys.stdout.flush()
    #print currencyCode


def getNewRecentMarketTrades(currencyCode,source):
    currency = getCurrencyFromDB(currencyCode)

    recentMarketTrades = getRecentMarketTrades(currencyCode,source)

    currencyTrades = currency["Data"][-1]["Trades"]

    #Get the last recorded trade time
    if len(currencyTrades)>0:
        lastRecordedTrade = datetime.datetime.strptime(currencyTrades[0]["trade_time"], "%Y-%m-%d %H:%M:%S")
    else:
        lastRecordedTrade = datetime.datetime(1, 1, 1, 0, 0)

    #lastRecordedTrade = datetime.datetime(1, 1, 1, 0, 0)
    #for trade in currencyTrades:
    #    tradeTime = datetime.datetime.strptime(trade["trade_time"], "%Y-%m-%d %H:%M:%S")
    #    if tradeTime > lastRecordedTrade:
    #        lastRecordedTrade = tradeTime

    newTrades = []
    newTradeCount = 0
    for trade in recentMarketTrades:
        tradeTime = datetime.datetime.strptime(trade["trade_time"], "%Y-%m-%d %H:%M:%S")
        if tradeTime > lastRecordedTrade:
            newTrades.append(trade)
            #newTrades.insert(0,trade)


    #updateCurrencyInDB(currency, currencyCode)
    #print "Updated " + currencyCode + " with " + str(newTradeCount) + " new trades"
    #print currencyTrades
    return newTrades

def getRecentMarketTrades(currencyCode,source):

    index_recentMarketTrades = source.find("self.recent_market_trades = ko.observableArray([")
    index1 = source.find("[",index_recentMarketTrades)
    index2 = source.find("]", index1)+1
    recentMarketTrades = source[index1:index2]


    #print recentMarketTrades
    if "trade_time" not in recentMarketTrades:
        #No trades
        recentMarketTrades = "[]"
    else:
        recentMarketTrades = parseToValidJson(recentMarketTrades)

    try:
        jsonData = json.loads(recentMarketTrades)
    except:
        e = sys.exc_info()[0]
        print "Err: %s" % e
        print "recentMarketTrades:" + recentMarketTrades

    return jsonData

def getAverageTradeValue(tradesData):
    total = 0
    count = 0
    if len(tradesData) > 0:
        for trade in tradesData:
            total = total + float(trade["trade_price"])
            count = count + 1
        average = total / count
        return '{:.8f}'.format(average)
    else:
        return -1



def getBuyOrders(currencyCode,source):

    index_recentMarketTrades = source.find("self.buy_orders = ko.observableArray([")
    index1 = source.find("[",index_recentMarketTrades)
    index2 = source.find("]", index1)+1
    buyOrders = source[index1:index2]


    #print recentMarketTrades
    if "price" not in buyOrders:
        #No trades
        buyOrders = "[]"
    else:
        buyOrders = parseToValidJson(buyOrders)

    try:
        jsonData = json.loads(buyOrders)
    except:
        e = sys.exc_info()[0]
        print "Err: %s" % e
        print "buyOrders:" + buyOrders

    ret = []
    i = 0
    for item in jsonData:
        ret.append(item)
        i = i+1
        if i == 10:
            break

    return ret

def getSellOrders(currencyCode,source):

    index_recentMarketTrades = source.find("self.sell_orders = ko.observableArray([")
    index1 = source.find("[",index_recentMarketTrades)
    index2 = source.find("]", index1)+1
    sellOrders = source[index1:index2]


    #print recentMarketTrades
    if "price" not in sellOrders:
        #No trades
        sellOrders = "[]"
    else:
        sellOrders = parseToValidJson(sellOrders)

    try:
        jsonData = json.loads(sellOrders)
    except:
        e = sys.exc_info()[0]
        print "Err: %s" % e
        print "buyOrders:" + sellOrders

    ret = []
    i = 0
    for item in jsonData:
        ret.append(item)
        i = i+1
        if i == 10:
            break

    return ret
