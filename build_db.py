from scrape import *
sys.path.append("/usr/local/lib/python2.7/site-packages")
import simplejson,json


print "Building database.."
market = getBitcoinTradingMarket()

#rebuild market with full list of trades
i = 0
for currency in market:

    addNewCurrencyToDB(currency)

    print str(i) + ": " + currency["MarketAssetCode"]
    i=i+1

print "Database built"
