# -*- coding: UTF-8 -*-

from flask import Flask

app = Flask(__name__)

app.config["SECRET_KEY"] = "JHdkj1;"
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///temp.db"
app.config["DEBUG"] = True
app.config['REPORT_CONFIG_DIR'] = "example/report_conf"

from flask.ext.babel import Babel

Babel(app)

from flask.ext.sqlalchemy import SQLAlchemy
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
