'''Configuration file - copy to settings.py and fill in your own settings.'''

SERVER_PORT = 2016
 
DATABASE = '/home/cw/causeway/causeway.db'

DEBUG = False

DATA_DIR = ''

# Price in BTC for 1MB storage and 50MB transfer
PRICE = 0.001

# RPC to Bitcoin Core
CORE_ENABLED = False
SERVER = '127.0.0.1'
RPCPORT = 8332
RPCUSER = 'bitcoinrpc'
RPCPASS = 'fill in with password from bitcoin.conf'
TESTNET = 'False'

# Minimum number of confirmations to consider a payment good 
MINCONF = 1
