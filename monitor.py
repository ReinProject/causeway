#!/usr/bin/env python

#
#    This file is part of osCommerce Bitcoin Payment Module
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import time
import re
import requests
import json
import signal
from requests.exceptions import ConnectionError
from time import sleep
from decimal import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Sale

# our configuration file - copy defaultsettings.py to settings.py and edit
from settings import * 
from rpc import RPC

# connect to db
engine = create_engine("sqlite:///" + DATABASE )
DBSession = sessionmaker(bind=engine)
session = DBSession()

# setup logging
import logging
logger = logging.getLogger('cw-monitor')
hdlr = logging.FileHandler('cw-monitor.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

# Daemon - handles running bitcoind and getting results back from it
class Daemon():
    def __init__(self):
        self.bitcoind_command  = ['bitcoind']
        self.rpc = RPC(RPCUSER, RPCPASS, SERVER, RPCPORT)

    def check(self):
        try:
            self.rpc.get('getinfo')
        except ConnectionError:
            logger.warning(json.dumps({'message': 'bitcoind not responding'}))

    def get_transactions(self,number):
        return self.rpc.get('listtransactions', ['*', int(number)])

    def get_accountaddress(self,account):
        return self.rpc.get('getaccountaddress', [account])

    def get_receivedbyaddress(self,address,minconf):
        res = self.rpc.get('getreceivedbyaddress', [address, int(minconf)])
        return Decimal(str(res['output']['result']))

    def get_balance(self,minconf):
        res = self.rpc.get('getbalance', ['*', int(minconf)])
        return Decimal(str(res))

    def send(self,address,amount):
        pass
        #res = rpc.get(['sendtoaddress',address,str(amount),'testing'])
        #return res


class Sales :
    def __init__(self):
        pass

    def enter_deposits(self):
        d = Daemon()
        unpaid = Sale.get_unpaid()
        logger.debug(json.dumps({"action":"enter deposits"}))

        # get list of pending orders with amounts and addresses
        for order in unpaid:
            # get total out
            total = Decimal(str(order.price))
            address = order.payment_address
            received = d.get_receivedbyaddress(address,MINCONF)
            logger.info(json.dumps({"action":"check received", "expected": str(total), "received": received, "address": address}))
            if( received >= total ):
                logger.info(json.dumps({"action":"payment complete", "order_id": str(order.id)}))
                # do things when payment received - mark a bucket paid, send an email, etc.
                order.paid = True
                session.commit()


if __name__ == "__main__":
    def signal_handler(signal, frame):
        logger.info(json.dumps({"message": "exit"}))
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info(json.dumps({"message": "start"}))

    d = Daemon()
    s = Sales()
    refreshcount = 0
    while(1):
        d.check()
        s.enter_deposits()
        refreshcount = refreshcount + 1
        REFRESH_PERIOD = 5
        sleep(REFRESH_PERIOD)
