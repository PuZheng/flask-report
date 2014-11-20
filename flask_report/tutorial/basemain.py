#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# basemain.py
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
# app.config['SQLALCHEMY_ECHO'] = True
Babel(app)

db = SQLAlchemy(app)
