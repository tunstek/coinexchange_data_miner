from scrape import *

#currencies = getDB()


#print json.dumps(currency, sort_keys=True, indent=4, separators=(',',': '))

totalEntryLength = 0.0
totalZeroVolumeEntries = 0.0

DBlength = getDBLen()
i = 0
while i < DBlength:
    currency = getDBIndex(i)
    #print currency
    print currency["MarketAssetCode"]
    print len(currency["Data"])
    totalEntryLength = totalEntryLength + len(currency["Data"])
    count = 0
    for entry in currency["Data"]:
    	if entry["Volume"] == "0.00000000":
    		count = count+1
    print "Zero volume count = " + str(count)
    totalZeroVolumeEntries = totalZeroVolumeEntries + count
    print "\n\n"
    i=i+1

print "Total entries = " + str(totalEntryLength)
print "Total zero volume entries = " + str(totalZeroVolumeEntries)
print "Percentage of zero volume entries = " + str((totalZeroVolumeEntries/totalEntryLength)*100) + "%"
print "Perhaps keeping this data may be beneficial (probably not though)"
#for currency in currencies:
#    print currency["MarketAssetCode"]
#    print len(currency["Data"])
#    print "\n\n"
#print currency
#for currency in db:
    #for entry in currency["Data"]:
    #    print len(entry)
    #print "\n\n"
