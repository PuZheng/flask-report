#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# basemain.py
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

db = SQLAlchemy(app)

from flask.ext import report
import models

report.FlaskReport(app, db, report.utils.collect_models(models))
