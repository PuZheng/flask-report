#! /usr/bin/env python
"""
SYNOPSIS
    python runserver.py [options]
OPTIONS
    -h
        show this help
    -p  <port>
        the port of server runs on, default is 5000
    -s  <host>
        the ip of the server runs on, default is '0.0.0.0'
"""
import sys
from getopt import getopt

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

db = SQLAlchemy(app)

if __name__ == '__main__':

    opts, _ = getopt(sys.argv[1:], 'hp:s:')

    for o, v in opts:

        if o == '-h':
            print __doc__
            sys.exit(1)
        elif o == '-p':
            port = int(v)
        elif o == '-s':
            host = v
        else:
            print 'unknown option: ' + o
            print __doc__
            sys.exit(1)

    try:
        port
        host
    except NameError:
        port = 5000
        host = '0.0.0.0'

    from utils import make_data
    make_data(db)

    app.run(debug=True, port=port, host=host)
