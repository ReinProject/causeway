#!/usr/bin/env python3
'''
Causeway Server - key/value storage server geared toward small files with ECSDA signature auth

Usage:
    python3 causeway-server.py
'''
import os, json, random, time, string
from settings import DATABASE, PRICE, DATA_DIR, SERVER_PORT

from flask import Flask
from flask import request
from flask import abort, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import and_

#from two1.lib.wallet import Wallet
#from two1.lib.bitserv.flask import Payment

from bitcoinecdsa import sign, verify
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
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
                 "pricing" : [{"rpc": "buy",
                               "per-req": 0,
                               "per-unit": PRICE,
                               "description": "1 MB hosting, 50 MB bandwidth, 1 year expiration"
                              },
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
                  "description": "This Causeway server provides microhosting services. Download the "\
                  "client and server at https://github.com/weex/causeway/archive/master.zip"
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

#@app.route('/buy')
#@payment.required(PRICE)
#def buy_hosting():
#    '''Registers one hosting bucket to account on paid request.'''
#    # extract account address from client request
#    owner = request.args.get('address')
#    contact = request.args.get('contact')
#
#    # check if user exists
#    o = db.session.query(Owner).get(owner)
#    if o is None:
#        # create them
#        o = Owner(owner)
#        db.session.add(o)
#        db.session.commit()
#
#    # owner should now exist,  create sale record for address
#    s = Sale(owner, contact, 1, 30, PRICE)
#    db.session.add(s)
#    db.session.commit()
#
#    body = json.dumps({'result': 'success', 
#                       'buckets': s.get_buckets()}, indent=2)
#    return (body, 200, {'Content-length': len(body),
#                        'Content-type': 'application/json',
#                       }
#           )

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

    count = db.session.query(Sale).filter(Sale.price == 0).count()
    if count < 4:
        s = Sale(owner, contact, 1, 30, 0)
        db.session.add(s)
        db.session.commit()
        body = json.dumps({'result': 'success', 
                           'buckets': s.get_buckets()}, indent=2)
    else:
        s = db.session.query(Sale).filter(and_(Sale.price == 0, Sale.owner == o.address)).first()
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
    #check if owner has an active sale record or request
    sales = db.session.query(Sale).filter(Sale.owner == owner).count()
    if sales == 0:
        body = json.dumps({"result": "error",
                          "message": "Account required to make queries"})
    elif string == 'mediators':
        mediator_query = Kv.query.filter(Kv.value.ilike('%Willing to mediate: True%')).paginate(1, 100, False)
        mediators = mediator_query.items
        res = []
        for m in mediators:
            res.append(m.value)
        body = json.dumps({"result": "success",
                          "mediators": res})
    elif string == 'jobs':
        q = Kv.query.filter(Kv.value.ilike('%Job name:%')).paginate(1, 100, False)
        items = q.items
        res = []
        for i in items:
            res.append(i.value)
        body = json.dumps({"result": "success",
                          string: res})
    elif string == 'in-process':
        worker = request.args.get('worker')
        q = Kv.query.filter(Kv.value.ilike('%Rein Offer%'+worker+'%')).paginate(1, 100, False)
        items = q.items
        res = []
        for i in items:
            res.append(i.value)
        body = json.dumps({"result": "success",
                          string: res})
    elif string == 'bids':
        # a bare sql query would look like:
        #      select * from bids inner join jobs on bid.job_id = job.job_id and job.owner == %s
        # instead we'll use a relationship where a bid has a job_id when we want tighter coupling
        q = Kv.query.filter(Kv.value.ilike('%Rein Bid%')).paginate(1, 100, False)
        items = q.items
        res = []
        for i in items:
            res.append(i.value)
        body = json.dumps({"result": "success",
                          string: res})
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
                kv = Kv(k, v, o, sale_id)
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

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=SERVER_PORT)
