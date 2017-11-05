
This was originally just an alert emailer before being upgraded to a data miner

# Setup

Run "python coinexchange_miner.py"

- For optional arguments run "python coinexchange_miner.py -h"

#### For email alerts:
Create a file named "send_email_config.py" and insert email credentials
 - See send_email_config_example.py for an example



## Issues
 - Getting intermediate "HTTP Error 403: Forbidden" errors in UpdateDatabase() possibly with getBitcoinTradingMarket()
