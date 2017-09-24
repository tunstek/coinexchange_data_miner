import os,sys

print "coinexchange.io Email Management Console"

cont = True
while cont:
    inp = raw_input("-->")

    inList = inp.split()

    if inList[0] == "add":
        if len(inList) != 6:
            print "ERR: Please use 'add [entry name] [MarketID] [buy price (unit)] [profit alert value (%)] [loss alert value (%)]' \nEmail alerts enabled by default."
        else:
            add_entryName = inList[1]
            add_marketId = inList[2]

            f = open("alert_list.csv","r")
            lines = f.readlines()
            f.close()

            write = True
            for line in lines:
                words = line.split(',')
                #Check for existing name entry
                if words[0] == add_entryName:
                    print "Err: Entry of the same name already exists!"
                    write = False
                    break
                elif words[1] == add_marketId:
                    print "Err: Entry of the same MarketID already exists!"
                    write = False
                    break

            if write:
                file = open("alert_list.csv" ,'a+')
                file.write(inList[1] + "," + inList[2] + "," + inList[3] + "," + inList[4] + "," + inList[5] + ",1" + "\n")
                file.close()
                print "Entry:" + inList[1] + " added."





    elif inList[0] == "remove":
        if len(inList) != 2:
            print "ERR: Please use 'remove [entry name OR MarketID]'"
        else:
            f = open("alert_list.csv","r")
            lines = f.readlines()
            f.close()
            f = open("alert_list.csv","w")
            for line in lines:
                lineList = line.split(',')
                write = True

                if lineList[0] == inList[1]: # The Name matches
                    inp = raw_input("Do you want to remove entry with the above name? (y/n)")
                    if inp == "y":
                        write = False
                elif lineList[1] == inList[1]: # The MarketID matches
                    inp = raw_input("Do you want to remove entry with the above MarketID? (y/n)")
                    if inp == "y":
                        write = False

                if write:
                    f.write(line)
                else:
                    print line[:-1] + " was removed." # removing the \n
            f.close()



    elif inList[0] == "list":
        f = open("alert_list.csv","r")
        lines = f.readlines()
        f.close()
        for line in lines:
            print line



    elif inList[0] == "close" or inList[0] == "exit" or inList[0] == "q":
        cont = False
    else:
        print "Unknown command"
        print "add [entry name] [MarketID] [buy price (unit)] [profit alert value (%)] [loss alert value (%)] - Adds tracking for a specified market \nremove [entry name OR MarketID] - Removes tracking for a specified market \nlist - Lists all alerts"
