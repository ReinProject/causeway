
from settings import *

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Owner(db.Model):
    __tablename__ = 'owner'

    address = db.Column(db.String(64), primary_key=True)
    delegate = db.Column(db.String(64))
    nonce = db.Column(db.String(32), unique=True)
    balance = db.Column(db.Integer)
    bad_attempts = db.Column(db.Integer)

    def __init__(self, address, delegate, nonce=None, balance=0, bad_attempts=0):
        self.address = address
        self.delegate = delegate
        self.nonce = nonce
        self.balance = balance
        self.bad_attempts = bad_attempts

    def __repr__(self):
        return '<Owner %r>' % self.address

class Kv(db.Model):
    __tablename__ = 'kv'

    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.String(8192))
    owner = db.Column(db.String(64))
    sale = db.Column(db.Integer)        #aka bucket
    testnet = db.Column(db.Boolean)

    def __init__(self, key, value, owner, sale, testnet=False):
        self.key = key
        self.value = value
        self.owner = owner
        self.sale = sale
        self.testnet = testnet

    def __repr__(self):
        return "<Kv %r>" % self.key

class Sale(db.Model):
    __tablename__ = 'sale'

    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(64))    # owner address
    contact = db.Column(db.String(255)) # owner's contact email address
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    term = db.Column(db.Integer)        # term in days
    amount = db.Column(db.Integer)      # units purchased
    price = db.Column(db.String(32))       # btc paid per unit
    paid = db.Column(db.Boolean)
    payment_address = db.Column(db.String(64))
    received = db.Column(db.String(32))
    bytes_used = db.Column(db.Integer)

    #s = Sale(owner, contact, 1, 30, PRICE)
    def __init__(self, owner, contact, amount, term, price, payment_address=None, id=None):
        self.owner = owner
        self.contact = contact
        self.amount = amount
        self.term = term
        self.price = price
        self.paid = 0
        self.payment_address = payment_address
        self.received = '0.0'
        self.bytes_used = 0
        self.id = id

    def get_buckets(self):
        sales = Sale.query.filter_by(owner=self.owner).all()
        result = []
        for s in sales:
            result.append({"id": s.id, "created":str(s.created), "bytes_free": str(1024*1024 - s.bytes_used)})
        return result

    @classmethod
    def get(cls, owner):
        return Sale.query.filter(cls.owner==owner, cls.payment_address != None).all()

    @staticmethod
    def get_recent(owner):
        return Sale.query.filter(Sale.owner==owner, Sale.payment_address != None,
                                 Sale.created > datetime.now()-timedelta(days=1)).all()

    @staticmethod
    def get_unpaid():
        return Sale.query.filter(Sale.paid == False,
                                 Sale.created > datetime.now()-timedelta(days=1)).all()

    def __repr__(self):
        return '<Sale %r>' % self.id
