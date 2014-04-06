# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask('pasticcio')
db = SQLAlchemy(app)
