from scrape import *
from send_email import *

import decimal
import os, sys, time, shutil, subprocess, datetime, json

sys.path.append("/usr/local/lib/python2.7/site-packages")





def main():


    print "*** Coinexchange Emailer ***"
    print time.strftime("%Y-%m-%d %H:%M")
    print "\n"
    


    # *********************************************************************
    # Bitcoin Stats
    # *********************************************************************

    try:
        bitcoinCurrentValStr = getBitcoinValue(0)
        bitcoinCurrentVal = decimal.Decimal(bitcoinCurrentValStr.replace(',', ''))
        bitcoinVal_1 = decimal.Decimal(getBitcoinValue(1))
    
        valueChange_1 = round((bitcoinCurrentVal - bitcoinVal_1) / abs(bitcoinCurrentVal) * 100,2)
        bitcoinVal_3 = decimal.Decimal(getBitcoinValue(3))
        valueChange_3 = round((bitcoinCurrentVal - bitcoinVal_3) / abs(bitcoinCurrentVal) * 100,2)
        bitcoinVal_7 = decimal.Decimal(getBitcoinValue(7))
        valueChange_7 = round((bitcoinCurrentVal - bitcoinVal_7) / abs(bitcoinCurrentVal) * 100,2)
        print "Bitcoin\nCurrent Value:"+bitcoinCurrentValStr+"\n1 day change:" + str(valueChange_1) + "%\n3 day change:" + str(valueChange_3) + "%\n7 day change:" + str(valueChange_7) + "%\n\n"
    except:
        print "Err collecting bitcoin info"



    # *********************************************************************
    # Main Loop
    # *********************************************************************

    while True:

        try:

          # *********************************************************************
          # Get New Currencies
          # *********************************************************************
  
            print "New Currencies:"
            newCurrencies = getNewCurrencies() #Returns the old market currency data
            for currency in  newCurrencies:
                print currency["MarketAssetCode"]
            details = ""
            if len(newCurrencies) != 0:
                for currency in newCurrencies:
                    lastPriceStr = currency["LastPrice"]
                    currencyCodeStr = currency["MarketAssetCode"]
                    details = details + currencyCodeStr + " - Last Traded at: " + lastPriceStr + "\nhttps://www.coinexchange.io/market/"+currencyCodeStr+"/BTC" + "\n"
  
                subjectNewCurrency = "NEW CURRENCY ALERT - coinexchange.io"
                bodyNewCurrency= "The following new currencies have been detected on coinexchange.io: \n\n" + details + "\n\n - coinexchange.io"
                send_alert(subjectNewCurrency, bodyNewCurrency)
            print "\n\n"
  



    
            # *********************************************************************
            # Process Alerts
            # *********************************************************************
    
            # Read the .csv for all active alerts
            f = open("alert_list.csv","r")
            lines = f.readlines()
            f.close()
    
            for line in lines[1:]:
    
                words = line.split(',')
                coinName = words[0]
                print coinName
    
                marketID = words[1]
    
                buyPrice = decimal.Decimal(words[2])
    
                profitThresholdPercentage = decimal.Decimal(words[3])
                lossThresholdPercentage = decimal.Decimal(words[4])
    
                lastPriceStr = getCurrencyDetail(marketID, "LastPrice")
                #lastPriceStr = "0.0000001" DEBUG
    
                lastPrice = decimal.Decimal(lastPriceStr)
    
                percentageChange = (lastPrice / buyPrice) * 100
    
    
                # buy @ 1
                # profitThresholdPercentage of 150 will alert @ 1.5
                # lossThresholdPercentage of 80 will alert @ 0.8
    
    
    
                subjectLoss = "LOSS ALERT - " + coinName + " - coinexchange.io"
                subjectProfit = "PROFIT ALERT - " + coinName + " - coinexchange.io"

                bodyLoss = "A below threshold loss has been detected on the following coin: " + coinName + "\nCurrent Value: " + str(round(percentageChange,2)) + "%" + " of buying price! \n\n coinexchange.io"
                bodyProfit = "An above threshold profit has been detected on the following coin: " + coinName + "\nCurrent Value: " + str(round(percentageChange,2)) + "%" + " of buying price! \n\n coinexchange.io"
    			
                emailAlertsEnabled = str(words[5][:-1])
    
    
                if percentageChange >= profitThresholdPercentage:
                    print "PROFIT - Last Price over Threshold!"
                    print "Buy Price:" + words[2]
                    print "Last Price:" + lastPriceStr
                    print "Percentage Profit Threshold:" + words[3] + "%"
                    print "Percentage Change: " + str(round(percentageChange,2)) + "%"
    
                    if emailAlertsEnabled == '1':
                        print "Sending email alert.."
                        send_alert(subjectProfit, bodyProfit)
                    else:
                        print "Email alerts disabled"
                    print "\n"
    
                elif percentageChange <= lossThresholdPercentage:
                    print "LOSS - Last Price below Threshold!"
                    print "Buy Price:" + words[2]
                    print "Last Price:" + lastPriceStr
                    print "Percentage Loss Threshold:" + words[4] + "%"
                    print "Percentage Change: " + str(round(percentageChange,2)) + "%"
    
                    if emailAlertsEnabled == '1':
                        print "Sending email alert.."
                        send_alert(subjectLoss, bodyLoss)
                    else:
                        print "Email alerts disabled"
                    print "\n"
    
                else:
                    print "Buy Price:" + words[2]
                    print "Last Price:" + lastPriceStr
                    print "Percentage Change: " + str(round(percentageChange,2)) + "%"
                    print "\n"

     		


     		# *********************************************************************
            # Database updates
            # *********************************************************************
      
            #need to check if new info links have been added
      
            print "Updating the database.."
            updateDB(newCurrencies)
            print "Database updated successfully.\n\n"



            # *********************************************************************
            # Check for currency price drops
            # *********************************************************************
            print "Checking for currency price drops.."
            currenciesNowAtOneSat = getCurrenciesNowTradingAtOneSat()
            if len(currenciesNowAtOneSat) > 0:

            	subjectInvestment = "INVESTMENT ALERT - coinexchange.io"
            	bodyInvestment = "A price drop to 1 sat has been detected on the following coins: \n"
            	
            	for currencyCode in currenciesNowAtOneSat:
            		bodyInvestment = bodyInvestment + currencyCode + " - https://www.coinexchange.io/market/"+currencyCode+"/BTC\n" 
            	bodyInvestment = bodyInvestment + "\ncoinexchange.io"

            	print "Investment alert for the following coins:"
            	print currenciesNowAtOneSat
            	print "Sending email alert.."
            	send_alert(subjectInvestment, bodyInvestment)
            print "Finished checking for price drops"




            



      
        except Exception, e:
        	print "Fatal ERR: "+str(e)+"\n\n"


        # repeat every 30 minutes (DOESN'T INCLUDE RUN TIME OF THE LOOP)
        time.sleep(1800)


        # USE THIS TO SHUTDOWN TO AVOID CORRUPTION

        
#************** END MAIN PROGRAM ***************






if __name__ == '__main__':
    main()
