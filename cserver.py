#!/usr/bin/env python3
'''
Causeway Server - key/value storage server geared toward small files with ECSDA signature auth

Usage:
    python3 causeway-server.py
'''
from flask import Flask
from flask import request
from flask import abort, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import and_

from settings import DATABASE_URI, PRICE, DATA_DIR, SERVER_PORT, DEBUG, TESTNET
import os
import json
import random
import time
import string
import requests
from decimal import Decimal

#from two1.lib.wallet import Wallet
#from two1.lib.bitserv.flask import Payment

from rpc import RPC
from bitcoinecdsa import sign, verify
from monitor import Daemon
from models import *
import bitcoin

if (TESTNET): bitcoin.SelectParams('testnet')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#wallet = Wallet()
#payment = Payment(app, wallet)

# start time
start_time = time.time()
stored = 0

@app.route('/')
@app.route('/help')
def home():
    '''Return service, pricing and endpoint information'''
    home_obj = [{"name": "causeway/1.freebeer",       # service 'causeway', version '1'
                 "pricing-type": "per-mb",   # pricing is listed per 1000000 bytes
                 "pricing" : [#{"rpc": "buy",
                              # "per-req": 0,
                              # "per-unit": PRICE,
                              # "description": "1 MB hosting, 50 MB bandwidth, 1 year expiration"
                              #},
                              {"rpc": "request",
                               "per-req": 0,
                               "per-unit": 0,
                               "description": "1 MB hosting, 50 MB bandwidth, 1 year expiration - free version for testing"
                              },
                              {"rpc": "get",
                               "per-req": 0,
                               "per-mb": 0
                              },
                              {"rpc": "put",
                               "per-req": 0,
                               "per-mb": 0
                              },

                              # default
                              {"rpc": True,        # True indicates default
                               "per-req": 0,
                               "per-mb": 0
                              }],
                  "description": "This Causeway server provides microhosting services."
                }
               ]

    body = json.dumps(home_obj, indent=2)

    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
                       )

@app.route('/status')
def status():
    '''Return general info about server instance. '''
    uptime = str(int(time.time() - start_time))
    st = os.statvfs(DATA_DIR)
    free = st.f_bavail * st.f_frsize
    body = json.dumps({'uptime': uptime,
                       'stored': str(stored),
                       'free': str(free),
                       'price': str(PRICE)
                      }, indent=2
                     )
    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/price')
def price():
    '''Return price for 1MB storage with bundled 50MB transfer.'''
    body = json.dumps({'price': 0})
    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/buy')
def buy_hosting():
    '''Registers one hosting bucket to account on paid request.'''
    # extract account address from client request
    owner = request.args.get('owner')
    delegate = request.args.get('delegate')
    contact = request.args.get('contact')


    # check if user exists
    o = db.session.query(Owner).get(owner)
    if o is None:
        # create them
        o = Owner(owner, delegate)
        db.session.add(o)
        db.session.commit()

    d = Daemon()
    res = d.get_accountaddress(owner)
    if 'result' in res and res['result'] == 'success':
        address = res['output']['result']
    else:
        body = json.dumps({'result': 'error',
                           'message': 'Error getting address. Contact server admin.'}, indent=2)
        return (body, 500, {'Content-length': len(body),
                            'Content-type': 'application/json',
                           }
               )

    # check if sale record exists
    # if recieved > 0, it will trigger bitcoin-cli to return a new address for this account
    #   so create a new Sale record
    # else we can just update thjis sale record's creation time, price, and receiving address
    # the policy here is you must pay with a single payment, if you send a payment and request 
    # a bucket, you will get a new address
    sales = Sale.get_recent(owner)
    if len(sales) == 0:
        s = Sale(owner, contact, 1, 30, PRICE, address)
        db.session.add(s)
        db.session.commit()
    else:
        for s in sales:
            if s.price == 0 or Decimal(s.received) > 0.0:
                continue

            s.created = db.func.current_timestamp()
            s.price = PRICE
            s.payment_address = address
            db.session.commit()
            break

    body = json.dumps({'result': 'success',
                       'address': address,
                       'price': str(PRICE),
                       'buckets': s.get_buckets()}, indent=2)
    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/request')
def request_hosting():
    '''Registers one hosting bucket to account on request (free for testing).'''
    # extract account address from client request
    owner = request.args.get('owner')
    delegate = request.args.get('delegate')
    contact = request.args.get('contact')

    # check if user exists
    o = db.session.query(Owner).filter(Owner.address == owner).first()
    print(o)
    if o is None:
        # create them
        o = Owner(owner, delegate)
        print(o)
        db.session.add(o)
        db.session.commit()

    count = db.session.query(Sale).filter(and_(Sale.price == 0, 
                                               Sale.owner == owner)).count()
    if count < 4:
        s = Sale(owner, contact, 1, 30, 0)
        db.session.add(s)
        db.session.commit()
        body = json.dumps({'result': 'success', 
                           'buckets': s.get_buckets()}, indent=2)
    else:
        s = db.session.query(Sale).filter(and_(Sale.price == 0,
                                               Sale.owner == owner)).first()
        body = json.dumps({'result': 'error',
                           'message': 'Maximum free buckets granted',
                           'buckets': s.get_buckets()}, indent=2)

    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/query', methods=['GET'])
def query():
    owner = request.args.get('owner')
    string = request.args.get('query')
    testnet = request.args.get('testnet')
    if testnet == 'True' or testnet == '1' or testnet == 1:
        testnet = True
    else:
        testnet = False
        
    #check if owner has an active sale record or request
    sales = db.session.query(Sale).filter(Sale.owner == owner).count()
    res = []
    if sales == 0:
        body = json.dumps({"result": "error",
                          "message": "Account required to make queries"})
        return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
               )
    elif string == 'mediators':
        mediator_query = Kv.query.filter(and_(Kv.testnet == testnet,
                                              Kv.value.ilike('%\nWilling to mediate: True%'))).paginate(1, 100, False)
        mediators = mediator_query.items
        for m in mediators:
            res.append(m.value)
    elif string == 'jobs':
        q = Kv.query.filter(and_(Kv.testnet == testnet,
                                 Kv.value.like('%\nRein Job%'))).paginate(1, 100, False)
        items = q.items
        for i in items:
            res.append(i.value)
    elif string == 'bids':
        q = Kv.query.filter(and_(Kv.testnet == testnet,
                                 Kv.value.like('%\nRein Bid%'))).paginate(1, 100, False)
        items = q.items
        for i in items:
            res.append(i.value)
    elif string == 'deliveries':
        job_creator = request.args.get('job_creator')
        q = Kv.query.filter(and_(Kv.testnet == testnet,
                                 Kv.value.ilike('%Rein Delivery%Job creator public key: '+job_creator+'%'))).paginate(1, 100, False)
        items = q.items
        for i in items:
            res.append(i.value)
    elif string == 'in-process':
        worker = request.args.get('worker')
        q = Kv.query.filter(and_(Kv.testnet == testnet,
                                 Kv.value.ilike('%Worker public key: '+worker+'%'))).paginate(1, 100, False)
        items = q.items
        for i in items:
            res.append(i.value)
    elif string == 'review':
        mediator = request.args.get('mediator')
        q = Kv.query.filter(and_(Kv.testnet == testnet,
                                 Kv.value.ilike('%Mediator public key: '+mediator+'%'))).paginate(1, 100, False)
        items = q.items
        for i in items:
            res.append(i.value)
    elif string == 'by_job_id':
        job_ids = request.args.get('job_ids')
        for job_id in job_ids.split(','):   
            q = Kv.query.filter(and_(Kv.testnet == testnet,
                                     Kv.value.ilike('%Job ID: '+job_id+'\n%'))).paginate(1, 100, False)
            items = q.items
            for i in items:
                if i is not None:
                    res.append(i.value)
    elif string == 'dispute':
        job_ids = request.args.get('job_ids')
        for job_id in job_ids.split(','):   
            last_len = len(res) 
            print(last_len)
            q = Kv.query.filter(Kv.value.ilike('%Rein Delivery%'+job_id+'\n%')).paginate(1, 100, False)
            items = q.items
            for i in items:
                if i is not None:
                    res.append(i.value)
            if len(res) == last_len: #we didn't find a delivery for this job id, look for an offer
                q = Kv.query.filter(Kv.value.ilike('%Rein Offer%'+job_id+'\n%')).paginate(1, 100, False)
                items = q.items
                for i in items:
                    if i is not None:
                        res.append(i.value)
            print(len(res))
    elif string == 'get_user_ratings':
        dest = None
        source = None
        try:
            dest = request.args.get('dest')

        except: pass

        try:
            source = request.args.get('source')

        except: pass

        if not dest and not source:
            res.append('error')

        else:
            q = Kv.query.filter(and_(Kv.testnet == testnet,
                                     Kv.value.like('%\nRein Rating%')))
            if dest:
                q = q.filter(Kv.value.like('%\nUser msin: {}%'.format(dest)))

            if source:
                q = q.filter(Kv.value.like('%\nRater msin: {}%'.format(source)))

            q = q.paginate(1, 100, False)
            items = q.items
            for i in items:
                res.append({'key': i.key, 'value': i.value})

    elif string == 'get_user_name':
        msin = request.args.get('msin')

        if not msin:
            res.append('error')

        else:
            q = Kv.query.filter(and_(Kv.testnet == testnet,
                                     Kv.value.like('%\nRein User Enrollment%'))).filter(Kv.value.like('%\nSecure Identity Number: {}%'.format(msin))).paginate(1, 100, False)
            items = q.items
            for i in items:
                res.append({'key': i.key, 'value': i.value})

    elif string == 'get_user':
      search_input = request.args.get('search_input')

      if not search_input:
        res.append('error')

      else:
        all_enrollments = Kv.query.filter(and_(
          Kv.testnet == testnet,
          Kv.value.like('%\nRein User Enrollment%')
        ))

        # Check for SIN matches
        q = all_enrollments.filter(
          Kv.value.like('%\nSecure Identity Number: {}%'.format(search_input))
        ).paginate(1, 20, False)

        # If unsuccessful, check for master address matches
        if not q.items:
          q = all_enrollments.filter(
            Kv.value.like('%\nMaster signing address: {}%'.format(search_input))
          ).paginate(1, 20, False)

        # If unsuccessful, check for delegate address matches
        if not q.items:
          q = all_enrollments.filter(
            Kv.value.like('%\nDelegate signing address: {}%'.format(search_input))
          ).paginate(1, 20, False)

        # If unsuccessful, check for username, case-insensitive, accepts partial matches
        if not q.items:
          q = all_enrollments.filter(
            Kv.value.ilike('%\nUser: %{}%'.format(search_input))
          ).paginate(1, 20, False)

        # If unsuccessful, check for contact, case-insensitive, accepts partial matches
        if not q.items:
          q = all_enrollments.filter(
            Kv.value.ilike('%\nContact: %{}%'.format(search_input))
          ).paginate(1, 20, False)

        for enrollment in q.items:
          res.append(enrollment.value)
                
    block_info = None
    if core_enabled:
        block_info = get_by_depth(12)
    body = json.dumps({"result": "success",
                       string: res,
                       "block_info": block_info})
    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/put', methods=['POST'])
def put():
    '''Store a key-value pair.'''
    # get size of file sent
    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return ("JSON Decode failed", 400, {'Content-Type':'text/plain'})

    k = in_obj['key']
    v = in_obj['value']
    o = in_obj['owner']
    n = in_obj['nonce']
    s = in_obj['signature']
    d = in_obj['signature_address']
    if 'testnet' in in_obj:
        testnet = in_obj['testnet']
    else:
        testnet = False

    owner = Owner.query.filter_by(address=o).first()
    if owner is None:
        body = json.dumps({'error': 'User not found'})
        code = 403
    elif owner.nonce != n:
        body = json.dumps({'error': 'Bad nonce'})
        code = 401
    elif not verify(d, k + v + d + n, s) :
        body = json.dumps({'error': 'Incorrect signature'})
        code = 401
    else:
        size = len(k) + len(v)

        # need to also check that we have an enrollment that makes this a delegate of this owner

        # check if owner has enough free storage
        # get free space from each of owner's buckets
        result = db.engine.execute('select * from sale where julianday("now") - \
                    julianday(sale.created) < sale.term order by sale.created desc')
        # choose newest bucket that has enough space
        sale_id = None
        for row in result:
            if (row[7] + size) < (1024 * 1024):
                sale_id = row[0]
    
        if sale_id is None:     # we couldn't find enough free space
            body = json.dumps({'error': 'Insufficient storage space.'})
            code = 403 
        else:
            # check if key already exists and is owned by the same owner
            kv = db.session.query(Kv).filter(and_(Kv.key == k, Kv.owner == o)).first()
            if kv is None:
                kv = Kv(k, v, o, sale_id, testnet)
                db.session.add(kv)
                db.session.commit()
            else:
                kv.value = v
                db.session.commit()
    
            s = db.session.query(Sale).get(sale_id)
            s.bytes_used = s.bytes_used + size
            db.session.commit()
            body = json.dumps({'result': 'success'})
            code = 201
    
    return (body, code, {'Content-length': len(body),
                        'Content-type': 'application/json',
                        }
           )

@app.route('/delete', methods=['POST'])
def delete():
    '''Delete a key-value pair.'''
    # Validate JSON body w/ API params
    try:
        body = request.data.decode('utf-8')
        in_obj = json.loads(body)
    except:
        return ("JSON Decode failed", 400, {'Content-Type':'text/plain'})

    k = in_obj['key']
    d = in_obj['address']
    n = in_obj['nonce']
    s = in_obj['signature']

    # check signature
    owner = Owner.query.filter_by(delegate=d).first()
    if owner.nonce not in n or verify(o, k + o + n, s):
        body = json.dumps({'error': 'Incorrect signature.'})
        code = 401
    else:
        # check if key already exists and is owned by the same owner
        kv = db.session.query(Kv).filter_by(key=k).filter_by(owner=o).first()
        if kv is None:
            body = json.dumps({'error': 'Key not found or not owned by caller.'})
            code = 404
        else:
            # free up storage quota and remove kv
            size = len(kv.value)
            sale_id = kv.sale
            s = db.session.query(Sale).get(sale_id)
            s.bytes_used = s.bytes_used - size
            db.session.delete(kv)
            db.session.commit()
            body = json.dumps({'result': 'success'})
            code = 200
    
    return (body, code, {'Content-length': len(body),
                         'Content-type': 'application/json',
                        }
           )

@app.route('/get')
def get():
    '''Get a key-value pair.'''
    
    key = request.args.get('key')

    kv = Kv.query.filter_by(key=key).first()

    if kv is None:
        body = json.dumps({'error': 'Key not found.'})
        code = 404
    else:
        body = json.dumps({'key': key, 'value': kv.value})
        code = 200

    # calculate size and check against quota on kv's sale record
    return (body, code, {'Content-length': len(body),
                        'Content-type': 'application/json',
                        }
           )

@app.route('/nonce')
def nonce():
    '''Return 32-byte nonce for generating non-reusable signatures..'''
    # check if user exists
    o = db.session.query(Owner).get(request.args.get('address'))
    if o is None:
        return abort(500)

    # clear the nonce by sending it to the server
    if request.args.get('clear') and request.args.get('clear') == o.nonce:
        o.nonce = ''
        db.session.commit()
        body = json.dumps({'nonce': o.nonce})
    # if nonce is set for user return it, else make a new one
    elif o.nonce and len(o.nonce) == 32:
        body = json.dumps({'nonce': o.nonce})
    # if not, create one and store it
    else:
        print("storing")
        n = ''.join(random.SystemRandom().choice(string.hexdigits) for _ in range(32))
        o.nonce = n.lower()
        db.session.commit()
        body = json.dumps({'nonce': o.nonce})

    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

@app.route('/address')
def get_deposit_address():
    '''Return new or unused deposit address for on-chain funding.'''
    # check if user exists
    o = db.session.query(Owner).get(request.args.get('address'))
    if o is None:
        return abort(500)

    address = request.args.get('address')
    message = request.args.get('contact') + "," + address
    signature = request.args.get('signature')

    print(len(signature))
    if len(signature) == 88 and verify(address, message, signature):
        body = json.dumps({'address': 'hereyago'})
    else:
        body = json.dumps({'error': 'Invalid signature'})

    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

def has_no_empty_params(rule):
    '''Testing rules to identify routes.'''
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route('/info')
def info():
    '''Returns list of defined routes.'''
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append(url)

    return json.dumps(links, indent=2)

@app.route('/bitcoin', methods=['GET', 'POST'])
def query_bitcoin():
    if not core_enabled:
        body = json.dumps({"result": "error",
                           "message": "Bitcoin Core not enabled for this server"})
        return (body, 200, {'Content-length': len(body),
                            'Content-type': 'application/json',
                           }
               )

    rpc = RPC(RPCUSER, RPCPASS, SERVER, RPCPORT)
    # to begin, get hash, block height, and time for latest, then n-blocks-ago, or for a block hash
    owner = request.args.get('owner')
    string = request.args.get('query')
    
    sales = db.session.query(Sale).filter(Sale.owner == owner).count()
    res = []
    out = {}
    if sales == 0:
        body = json.dumps({"result": "error",
                           "message": "Account required to make queries"})
        return (body, 200, {'Content-length': len(body),
                            'Content-type': 'application/json',
                           }
               )
    elif string == 'getbydepth':
        depth = request.args.get('depth')
        res = rpc.get('getblockcount')
        if 'output' in res and 'result' in res['output']:
            height = res['output']['result'] - int(depth)
    elif string == 'getbyheight':
        height = request.args.get('height')
    elif string == 'getbyhash':
        res = rpc.get('getblockheader', [request.args.get('hash')])
        height = res['output']['result']['height']
    elif string == 'sendrawtransaction':
        tx = request.args.get('tx')
        res = rpc.get('sendrawtransaction', [str(tx)])
        if 'output' in res and 'result' in res['output']:
            out['txid'] = res['output']['result']
            body = json.dumps(out)
            return (body, 200, {'Content-length': len(body), 'Content-type': 'application/json', })
        
    res = rpc.get('getblockhash', [int(height)])
    out['height'] = height
    if 'output' in res and 'result' in res['output']:
        out['hash'] = res['output']['result']
        res = rpc.get('getblockheader', [str(out['hash'])])
        out['time'] = res['output']['result']['time']
        out['height'] = height
        body = json.dumps(out)
    else:
        body = json.dumps({"result": "error",
                           "message": "Invalid depth or RPC error"})
    return (body, 200, {'Content-length': len(body),
                        'Content-type': 'application/json',
                       }
           )

def get_by_depth(depth):
    rpc = RPC(RPCUSER, RPCPASS, SERVER, RPCPORT)
    res = rpc.get('getblockcount')
    if 'output' in res and 'result' in res['output']:
        height = res['output']['result'] - int(depth)
    else:
        return None
    res = rpc.get('getblockhash', [height])
    out = {}
    if 'output' in res and 'result' in res['output']:
        out['hash'] = res['output']['result']
        res = rpc.get('getblockheader', [out['hash']])
        out['time'] = res['output']['result']['time']
        out['height'] = height
    return out

if __name__ == '__main__':
    if DEBUG:
        app.debug = True

    rpc = RPC(RPCUSER, RPCPASS, SERVER, RPCPORT)
    try:
        rpc.get('getblockcount')
        core_enabled = CORE_ENABLED
    except:
        core_enabled = False

    print("Core enabled: " + str(core_enabled))

    app.run(host='0.0.0.0', port=(os.environ.get('SERVER_PORT', SERVER_PORT)))
    #app.run(host='127.0.0.1', port=SERVER_PORT)
