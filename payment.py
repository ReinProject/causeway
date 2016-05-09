from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from settings import DATABASE, PRICE, DATA_DIR, SERVER_PORT, DEBUG

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
manager = Manager(app)

@manager.command
def process():
    # list transactions is what we want to do. pull in the monitor code.

if __name__ == "__main__":
    manager.run()
