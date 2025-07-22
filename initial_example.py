from lnmarkets import rest
import os

options = {'key': os.getenv('LN_MARKETS_KEY'), 
           'secret': os.getenv('LN_MARKETS_SECRET'), 
           'passphrase': os.getenv('LN_MARKETS_PASSPHRASE'),
           'network': 'testnet'}

lnm = rest.LNMarketsRest(**options)

lnm.futures_get_ticker()
